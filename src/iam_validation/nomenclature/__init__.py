"""Package to read and use definitions and mappings for IAM COMPACT."""
import functools
import typing as tp

from .. import type_helpers

from . import defs
from . import mapping
from . import validation

from .defs import (
    MergedDefs,
    NomenclatureDefs,
)



COMMON_DEFINITIONS_URL: tp.Final[str] \
    = 'https://github.com/IAMconsortium/common-definitions.git'
"""The URL of the `common-definitions` repository."""
