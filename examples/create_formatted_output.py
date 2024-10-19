# %% [markdown]
# # Create formatted output from criterion target comparisons
#
# This example shows how to use the `iam_validation.targets` package to create
# formatted output from target comparisons made with the `.criteria` and
# `.targets` subpackages.

# %% [markdown]
# Imports

# %%
from iam_validation.output import TimeseriesRefTargetOutput
from .compare_timeseries_ref_data import target_range, model_df

import pandas as pd


# %% [markdown]
# Create an outputter object that can produced styled output, and use it to get
# a formatted DataFrame. The returned DataFrame will have colored highlights for
# the ratios that fall outside the allowed range.
#
# Using `with_summary=True` gives us a dict with two elements:
# - `"summary"`: A pandas DataFrame with the maximum deviation per variable,
#   model, scenario and region.
# - `"full_comparison"`: A wide DataFrame with the ratios for each variable,
#   model, scenario, region, and *year*.

# %%
ratios_outputter = TimeseriesRefTargetOutput(target_range)
ratios_styled_dfs: dict[str, pd.DataFrame] \
    = ratios_outputter.prepare_output(model_df, with_summary=True)


# %% [markdown]
# Write the output to an Excel file, which will have colored cells for
# deviations outside the range. The option `with_summary=True` will produces two
# worksheets, one with summmary and one with full comparison (mirroring the dict
# produced in the previous step).

# %%
ratios_outputter.to_excel('comparison.xlsx')
