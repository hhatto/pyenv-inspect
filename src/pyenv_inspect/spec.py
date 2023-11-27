from __future__ import annotations

import enum
import re
from typing import NamedTuple, Optional

from .exceptions import SpecParseError, UnsupportedImplementation
from .version import VERSION_PATTERN


class Implementation(enum.Enum):
    CPYTHON = 'cpython'
    PYPY = 'pypy'
    UNSUPPORTED = 'unsupported'


CPYTHON_SPEC_REGEX = re.compile(
    rf'(?P<version>{VERSION_PATTERN})'
)
PYPY_VERSION_PATTERN = (
    r'(?P<pypybase>\d(?:\.\d+){0,2})')
PYPY_SPEC_REGEX = re.compile(
    rf'(?P<version>{VERSION_PATTERN}-{PYPY_VERSION_PATTERN})'
)


class PyenvPythonSpec(NamedTuple):
    """Contains specification about a Python Interpreter"""
    string_spec: str
    implementation: Implementation
    version: Optional[str]

    @classmethod
    def from_string_spec(cls, string_spec: str) -> Optional[PyenvPythonSpec]:
        is_cpython = string_spec[0].isdigit()
        is_pypy = string_spec.startswith('pypy')
        if is_cpython:
            implementation = Implementation.CPYTHON
            match = CPYTHON_SPEC_REGEX.fullmatch(string_spec)
            if not match:
                raise SpecParseError
            version = match.group('version')
        elif is_pypy:
            implementation = Implementation.PYPY
            version_string = string_spec[4:]
            match = PYPY_SPEC_REGEX.fullmatch(version_string)
            if not match:
                raise SpecParseError
            version = match.group('version')
        else:
            implementation = Implementation.UNSUPPORTED
            version = None
        return cls(string_spec, implementation, version)

    def to_dict(self) -> dict:
        return {
            'string_spec': self.string_spec,
            'implementation': self.implementation.value,
            'version': self.version,
        }

    def is_supported(self, *, raise_exception: bool = False) -> bool:
        supported = self.implementation in (Implementation.CPYTHON, Implementation.PYPY)
        if not supported and raise_exception:
            raise UnsupportedImplementation
        return supported
