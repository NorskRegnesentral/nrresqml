import typing
import inspect
from typing import Type, Optional

from lxml import etree

from nrresqml import reporting
from nrresqml.structures import relationships, contenttypes, xsd, energetics, core
from nrresqml.structures.resqml import properties, common, geometry, representations


_packages = [
    relationships,
    contenttypes,
    xsd,
    energetics,
    core,
    # ResQml specific
    properties,
    common,
    geometry,
    representations
]


_classes = {
    m: inspect.getmembers(m, inspect.isclass)
    for m in _packages
}


_xsi_type_uri = f'{{{xsd.xsi_uri}}}type'


class _ElementExtractValueError(Exception):
    pass


def _lookup_xsi_type(xsi_name: str) -> Optional[Type]:
    for module, clazzes in _classes.items():
        for clazz, type_ in clazzes:
            if type_.__module__ != module.__name__:
                continue
            try:
                ns = [f'{type_.main_namespace(abbreviate=True)}:',
                      f'{{{type_.main_namespace(abbreviate=False)}}}']
            except (AttributeError, NotImplementedError):
                ns = ['']
            if any(xsi_name == f'{n}{clazz}' for n in ns):
                return type_
    return None


def _determine_type(el: etree.Element) -> Optional[Type]:
    t = el.attrib.get(_xsi_type_uri)
    if t is None:
        raise NotImplementedError('')
    else:
        return _lookup_xsi_type(t)


def _iterate_attributes(type_: Type):
    for an, at in typing.get_type_hints(type_).items():
        yield an


def _find_child_values(el: etree.Element, tag_end: str) -> typing.List[typing.Any]:
    """
    Look up all values for a given tag on the provided etree.Element. However, the tag is interpreted as the end of a
    tag, which enabled look-up for tags while ignoring namespace if desired.
    """
    # Initialize 'out' with values from the element's attributes
    out = [value
           for key, value in el.attrib.items()
           # For attributes we ignore the namespace
           if tag_end.endswith(key)]
    # Append values from the element's children
    for child in el:
        if not child.tag.endswith(tag_end):
            continue
        if child.text is not None and child.text.strip() != '':
            txt = child.text.strip()
            ty = _determine_type(child)
            if issubclass(ty, xsd.BasicEnum):
                out.append(getattr(ty, txt))
            else:
                out.append(ty(txt))
        else:
            out.append(objectify(child))
    return out


def _is_optional(type_):
    orig = getattr(type_, '__origin__', None)
    return orig is typing.Union and isinstance(None, type_.__args__)


def _extract_values(el: etree.Element, att_name: str, att_type: Type
                    ) -> typing.Union[typing.List[typing.Any], typing.Any]:
    out = _find_child_values(el, att_name)
    # NB! This does not handle Optional[List]
    if getattr(att_type, '__origin__', None) is list:
        return out
    elif len(out) > 1:
        raise _ElementExtractValueError(f'Multiple elements found for tag {att_name}')
    elif _is_optional(att_type):
        return out
    elif len(out) == 0:
        raise _ElementExtractValueError(f'Failed to find tag {att_name}')
    else:
        return out[0]


def _iterate(el: etree.Element):
    for key, value in el.attrib.items():
        if key == _xsi_type_uri:
            continue
        yield key, value
    type_ = _determine_type(el)
    for an, at in typing.get_type_hints(type_).items():
        try:
            yield an, _extract_values(el, an, at)
        except _ElementExtractValueError as e:
            reporting.error(str(e))


def objectify(el: etree.Element):
    # TODO: avoid calling determine_type twice
    type_ = _determine_type(el)
    if type_ is None:
        reporting.error(f'Failed to determine type for XML tag {el.tag}')
        return
    ctor_dict = dict(_iterate(el))
    return type_(**ctor_dict)
