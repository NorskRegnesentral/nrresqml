from dataclasses import is_dataclass
from typing import List
from nrresqml.structures.energetics import AbstractObject, DataObjectReference
from nrresqml import reporting


def resolve_references(obj, refs: List[AbstractObject]):
    for an in dir(obj):
        if an.startswith('_'):
            continue
        ao = getattr(obj, an)
        if isinstance(ao, DataObjectReference):
            ds = [r for r in refs if r.uuid == ao.UUID]
            if len(ds) == 0:
                reporting.error(f'A DataObjectReference is referring a non-existing object ({ao.UUID})')
                continue
            if len(ds) > 1:
                reporting.error(f'A DataObjectReference is referring a duplicate uuid ({ao.UUID})')
                continue
            d = ds[0]
            setattr(obj, an, d)
            resolve_references(d, refs)
        elif is_dataclass(ao):
            resolve_references(ao, refs)
