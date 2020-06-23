from enum import Enum
from typing import List, Tuple, Any, Optional
import datetime


xsi_uri = 'http://www.w3.org/2001/XMLSchema-instance'


class _GeneralType:
    @classmethod
    def main_namespace(cls, abbreviate) -> str:
        if len(cls.namespaces()) == 0:
            return ''
        ns = cls.namespaces()[0]
        return ns[0] if abbreviate else ns[1]

    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        raise NotImplementedError('Method not implemented by subclass')

    @classmethod
    def type_name(cls) -> str:
        return cls.__name__

    @classmethod
    def full_type_name(cls, abbreviate_ns=False) -> str:
        if abbreviate_ns:
            prefix = f'{cls.main_namespace(abbreviate=True)}:'
        else:
            prefix = f'{{{cls.main_namespace(abbreviate=False)}}}'
        return f'{prefix}{cls.type_name()}'


class XsdComplexType(_GeneralType):
    @classmethod
    def content_type_string(cls) -> str:
        return f'application/x-resqml+xml;version=2.0.1;type=obj_{cls.type_name()}'

    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [('xsi', 'http://www.w3.org/2001/XMLSchema-instance')]

    @classmethod
    def xml_attributes(cls) -> List[str]:
        """ Returns a list of names of attributes that will be added as XML attributes instead of nodes """
        return []


class BasicType(_GeneralType):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        raise NotImplementedError('Method not implemented by subclass')


class BasicEnum(BasicType, Enum):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        raise NotImplementedError('Method not implemented by subclass')


class XsdBasicType(BasicType):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [('xsi', 'http://www.w3.org/2001/XMLSchema-instance')]


class integer(XsdBasicType, int):
    pass


class nonNegativeInteger(integer):
    def __new__(cls, value) -> Any:
        value = int(value)
        assert value >= 0
        return super().__new__(cls, value)


class positiveInteger(integer):
    def __new__(cls, value) -> Any:
        value = int(value)
        assert value > 0
        return super().__new__(cls, value)


class double(XsdBasicType, float):
    pass


class string(XsdBasicType, str):
    pass


class boolean(XsdBasicType, int):
    def __new__(cls, value) -> Any:
        return super().__new__(cls, bool(value))


class dateTime(XsdBasicType, datetime.datetime):
    _fmt = "%Y-%m-%dT%H:%M:%SZ"

    def __new__(cls, *args, **kwargs) -> Any:
        if len(args) == 1 and isinstance(args[0], str):
            dt = datetime.datetime.strptime(args[0], cls._fmt)
            return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        else:
            return super().__new__(cls, *args, **kwargs)

    def __str__(self) -> str:
        return self.strftime(self._fmt)
