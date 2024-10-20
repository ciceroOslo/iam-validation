from iam_validation.nomenclature import NomeclatureDefs, MergedDefs, COMMON_DEFINITIONS_URL
from pathlib import Path
import pyam, pandas as pd

# Get variable and region names from `common_definitions`
common_defs = NomeclatureDefs.from_url(COMMON_DEFINITIONS_URL, region_mappings=False)

# Get project-specific names for all dimensions, and region-mappings
project_defs = NomenclatureDefs.from_url(repo_url, dimensions=['model', 'scenario',
                                                               'region', 'variable'])
# Merge the definitions, and use project-specific definitions where they overlap
merged_defs: MergedDefs = common_defs.update(project_defs)

# Load a file with model results as an IAMC-formatted Excel or CSV file.
model_df = pyam.IamDataFrame('./my_model_output.xlsx')

# Get invalid names, including recognized model-native ones. Returns a dict with dimension
# names as keys, and invalid names or combos as lists or DataFrames
invalid_names: dict[str, list[str]|pd.DataFrame] = \
    merged_defs.get_invalid_names(model_df, raw_model_regions=True)

# Get invalid unit/variable combos. Returns a DataFrame, with one row for each known
# variables that has unrecognized units, and columns with lists of the unrecognized units for
# each variable, and one lists of the valid unit names for that variable.
invalid_units: pd.DataFrame = merged_defs.get_invalid_variable_units(model_df)
