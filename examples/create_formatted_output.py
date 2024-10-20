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
from compare_timeseries_ref_data import target_range, model_df

import pandas as pd
from pandas.io.formats.style import Styler


# %% [markdown]
# Create an outputter object that can produce styled output, and use it to get
# formatted DataFrames. The returned DataFrames will have colored highlights for
# the ratios that fall outside the allowed range.
#
# The `.prepare_styled_output` method of `TimeseriesRefTargetOutput` gives us a
# dict with two elements:
# - `"summary"`: A pandas DataFrame with the maximum deviation per variable,
#   model, scenario and region.
# - `"full_comparison"`: A wide DataFrame with the ratios for each variable,
#   model, scenario, region, and *year*.

# %%
ratios_outputter = TimeseriesRefTargetOutput(target_range)
ratios_styled_dfs: dict[str, Styler] \
    = ratios_outputter.prepare_styled_output(model_df)


# %% [markdown]
# Write the output to an Excel file, which will have colored cells for
# deviations outside the range. The file will have two worksheets, one with
# summary and one with full comparison (mirroring the dict produced in the
# previous step).

# %%
ratios_outputter.to_excel('comparison.xlsx', results=ratios_styled_dfs)
