# %% [markdown]
# # Compare model output data with reference data
#
# This example shows how to use the `iam-validation` subpackages `.criteria` and
# `.targets` to compare model output data with timeseries reference data,
# including detailed comparison for each data point (model, scenario, region, 
# variable and year) that is present in both the model output and in the
# reference data.

# %% [markdown]
# Import the required packages

# %%
from iam_validation.criteria import TimeseriesRefCriterion
from iam_validation.targets import CriterionTargetRange

from pathlib import Path

import pandas as pd
import pyam


# %% [markdown]
# Load your reference timeseries data for one or more variables (e.g, data to be
# used for harmonization), which needs to be prepared in IAMC format and
# loadable with `pyam`. Replace `referenc_file` below with the path to your
# reference timeseries data, as a string or `pathlib.Path` object.

# %%
reference_file: Path|str = Path('.') / 'my_reference_data.xlsx'
ref_data = pyam.IamDataFrame(reference_file)


# %% [markdown]
# Create a timeseries reference object that compares model results to the
# reference data by taking the ratio, and define an allowed target range of
# +/- 5%. The `criterion_name` can be any string, bu should be recognizable (can
# be used by output functions later). Comparisons are here made for each
# variable, region and year that are present in both the model output and the
# reference data.

# %%
timeseries_ref = TimeseriesRefCriterion(
    criterion_name='Reference data ratio comparison',
    reference=ref_data,
    comparison_function='ratio',
    broadcast_dims=('model', 'scenario'),
)
target_range = CriterionTargetRange(
    criterion=timeseries_ref,
    target=1.0,
    range=(0.95, 1.05),
)


# %% [markdown]
# Load the model data that you want to compare to the reference data, from an
# IAMC-formatted Excel or CSV file.

# %%
model_file: Path|str = Path('.') / 'my_model_output.xlsx'
model_df = pyam.IamDataFrame(model_file)


# %% [markdown]
# Get a pandas.Series with the ratios of model data relative reference data

# %%
comparison_ratios: pd.Series = timeseries_ref.get_values(model_df)


# %% [markdown]
# Get a pandas.Series with True/False for what data points are inside the
# allowed target range.

# %%
in_range_statuses: pd.Series = target_range.get_in_range(model_df)

