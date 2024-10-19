"""Helper functions for type-checking and working with type annotations."""
from typing import TypeVar



TV = TypeVar('TV')

class IsNoneError(ValueError):
    """Raised when a value is None."""
    ...
###END class IsNoneError

def not_none(
        x: TV|None,
) -> TV:
    """Returns a value if None, otherwise raises an IsNoneError"""
    if x is None:
        raise IsNoneError()
    return x
###END def not_none

