from nrresqml.structures import xsd

import nrresqml.factories.energetics
import nrresqml.factories.resqml.relationships
from nrresqml.derivatives.utils import iterate_attributes
from typing import List, Tuple, Union, Optional

from lxml import etree
from nrresqml.structures.energetics import AbstractObject, DataObjectReference


def _data_object_reference_to_element(obj: DataObjectReference, tag: str) -> etree.Element:
    return elementify(obj, [], tag)


def _create_data_object_reference(att_name: str, obj: AbstractObject, parent_ns: str) -> etree.Element:
    r = nrresqml.factories.energetics.reference(obj)
    el = _data_object_reference_to_element(r, _full_tag(parent_ns, att_name))
    return el


def _append_xsi_type(el: etree.Element, obj: Union[xsd.BasicType, xsd.XsdComplexType]):
    el.attrib[f'{{{xsd.xsi_uri}}}type'] = obj.full_type_name(abbreviate_ns=True)


def _full_tag(ns, att):
    # NB! Currently, ignore namespace for readability
    return f'{att}'


def _objectify_basic_attribute(att_name, att_obj, parent_ns) -> etree.Element:
    full_tag = _full_tag(parent_ns, att_name)
    if isinstance(att_obj, xsd.BasicType):
        ns = dict(att_obj.namespaces())
        el = etree.Element(full_tag, nsmap=ns)
    else:
        el = etree.Element(full_tag)
    if isinstance(att_obj, xsd.BasicEnum):
        el.text = att_obj.name
    else:
        el.text = str(att_obj)
    _append_xsi_type(el, att_obj)
    return el


def _attributify(att_name, att_obj) -> Tuple[str, str]:
    return att_name, str(att_obj)


def elementify(obj: xsd.XsdComplexType, existing_refs: List[AbstractObject], tag: Optional[str]) -> etree.Element:
    # el = etree.Element(obj.full_type_name(), nsmap=dict(obj.namespaces()))
    tag = tag or obj.full_type_name()
    el = etree.Element(tag, nsmap=dict(obj.namespaces()))
    for att, att_obj in iterate_attributes(obj):
        if att in obj.xml_attributes():
            key, value = _attributify(att, att_obj)
            el.attrib[key] = value
        elif isinstance(att_obj, xsd.XsdComplexType) and att_obj not in existing_refs:
            # Object is complex and needs to be recursively objectified
            el.append(elementify(att_obj, existing_refs, att))
        elif att_obj in existing_refs:
            # Object should only be addressed by reference since it already exists
            el.append(_create_data_object_reference(att, att_obj, obj.main_namespace(abbreviate=False)))
        else:
            # Object is simple and can be translated without recursion
            el.append(_objectify_basic_attribute(att, att_obj, obj.main_namespace(abbreviate=False)))
    # Inject the xsi type name
    _append_xsi_type(el, obj)
    return el
