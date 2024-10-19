# %% [markdown]
# # Find invalid names and variable/unit combinations
#
# This example shows how to use the `iam_validation.nomenclature` package to
# detect invalid names and variable/unit combinations in your IAM output.
#
# The model output must be in a file that can be read into a `pyam.IamDataFrame`
# object by the `pyam` package, i.e., an Excel or CSV file in IAMC format.

# %%
# Import required classes from the `iam_validation.nomenclature` package,
# and required modules/classes from `pandas` and `pyam`.

from iam_validation.nomenclature import (
    NomeclatureDefs,
    MergedDefs,
    COMMON_DEFINITIONS_URL,
)
import pandas as pd
from pathlib import Path
import pyam


# %%
# Get variable and region names from `common_definitions`, but *not* region
# aggregation mappings from model-native to common regions. We will use mappings
# from our own project definitions instead.

common_defs = NomeclatureDefs.from_url(COMMON_DEFINITIONS_URL,
                                       region_mappings=False)

# %%
# Get project-specific names for all dimensions, and region-mappings from custom
# project definitions

project_defs = NomenclatureDefs.from_url(
    repo_url,
    dimensions=['model', 'scenario', 'region', 'variable'],
)

# %%
# Merge the definitions. Let project-specific definitions override
# `common-definitions` where they overlap.

merged_defs: MergedDefs = common_defs.update(project_defs)


# %%
# Now load a file with model results. Set `results_file` below to a path to your
# model results, as an IAMC-formatted Excel or CSV file. Can be either a string
# or a `pathlib.Path` object.
results_file: Path|str = Path('.') / 'my_model_output.xlsx'
model_df = pyam.IamDataFrame(results_file)


# %%
# Get invalid names, including recognized model-native ones. Returns a dict with
# dimension names as keys, and invalid names for each dimension as a list, or
# as a DataFrame of invlid model/region-name pairs when recognizing unammped
# model-native region names.

invalid_names: dict[str, list[str]|pd.DataFrame] = \
    merged_defs.get_invalid_names(model_df, raw_model_regions=True)


# %%
# Get invalid unit/variable combos. Returns a DataFrame, where the index is
# known variables that have unrecognized units, with one column with lists of
# the unrecognized units for each variable, and one column with lists of the
# valid unit names for that variable.

invalid_units: pd.DataFrame = merged_defs.get_invalid_variable_units(model_df)
