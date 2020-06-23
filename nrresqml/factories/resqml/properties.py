from typing import Dict

from nrresqml.factories.resqml.common import create_meta_data
from nrresqml.structures import xsd
from nrresqml.structures.energetics import EpcExternalPartReference, Hdf5Dataset
from nrresqml.structures.resqml import properties as ps
from nrresqml.structures.resqml.geometry import DoubleHdf5Array, IntegerHdf5Array
from nrresqml.structures.resqml.properties import StringTableLookup, StringLookup
from nrresqml.structures.resqml.representations import AbstractRepresentation, IndexableElements


def create_continuous_property(title: str, h5_path: str, min_value: float, max_value: float,
                               rep: AbstractRepresentation, h5p: EpcExternalPartReference,) -> ps.ContinuousProperty:
    """
    Creates a continuous property that is related to some other supporting representation. Convenience factory function
    that fills in default values where appropriate. These can be overwritten post-construction
    """
    meta = create_meta_data(title)
    a_kind = ps.StandardPropertyKind(ps.ResqmlPropertyKind.volume_per_volume)
    h5d = Hdf5Dataset(xsd.string(h5_path), h5p)
    ava = DoubleHdf5Array(h5d)
    pov = ps.PatchOfValues(xsd.integer(0), ava)
    prop = ps.ContinuousProperty(
        IndexableElement=IndexableElements.cells,
        Count=xsd.positiveInteger(1),
        RealizationIndex=None,
        TimeStep=None,
        SupportingRepresentation=rep,
        PropertyKind=a_kind,
        PatchOfValues=pov,
        MinimumValue=xsd.double(min_value),
        MaximumValue=xsd.double(max_value),
        Uom=ps.ResqmlUom.m,
        **meta
    )
    return prop


def create_categorical_property(title: str, h5_path: str, rep: AbstractRepresentation, h5p: EpcExternalPartReference,
                                value_map: Dict[int, str]) -> ps.CategoricalProperty:
    meta = create_meta_data(title)
    a_kind = ps.StandardPropertyKind(ps.ResqmlPropertyKind.categorical)
    h5d = Hdf5Dataset(xsd.string(h5_path), h5p)
    assert -1 not in value_map  # Not supported
    ava = IntegerHdf5Array(h5d, xsd.integer(-1))
    pov = ps.PatchOfValues(xsd.integer(0), ava)
    # Look-up table
    tab_meta = create_meta_data(f'{title} - look-up')
    values = [
        StringLookup(xsd.integer(key), xsd.string(value))
        for key, value in value_map.items()
    ]
    tab = StringTableLookup(Value=values, **tab_meta)
    prop = ps.CategoricalProperty(
        IndexableElement=IndexableElements.cells,
        Count=xsd.positiveInteger(1),
        RealizationIndex=None,
        TimeStep=None,
        SupportingRepresentation=rep,
        PropertyKind=a_kind,
        PatchOfValues=pov,
        Lookup=tab,
        **meta
    )
    return prop
