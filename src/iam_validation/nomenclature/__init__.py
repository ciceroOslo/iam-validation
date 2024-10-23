"""Package to read and use definitions and mappings for IAM COMPACT."""
import functools

# Import _region_adjustments to make sure region attributes are adjusted as
# needed before the definitions are loaded.
# Change: Don't adjust for regions yet. Since the ISO3 code check in
# `nomenclature.RegionCode` happens directly against the ISO2 codes in
# `pycountry.countries`, making adjustments here won't be enough. Need to wait
# until the `nomenclature` code is changed, if ever.
# from . import _region_adjustments

from .. import type_helpers

from . import defs
from . import mapping
from . import validation
