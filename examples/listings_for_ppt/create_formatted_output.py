from iam_validation.output import TimeseriesRefTargetOutput

import pandas as pd
from pandas.io.formats.style import Styler

# Create an outputter object that can produce styled output, using the `CriterionTargetRange`
# object `target_range` and the model data `model_df` from the previous example.
# `TimeseriesRefTargetOutput.prepare_styled_output` gives us a dict with two elements:
# - "summary": A styled pandas DataFrame with the maximum deviation per variable,
#   model, scenario and region.
# - "full_comparison": A wide styled DataFrame with the ratios for each variable, model,
#   scenario, region, and *year*.
# The DataFrames have colored highlights for the ratios that fall outside the allowed range.
ratios_outputter = TimeseriesRefTargetOutput(target_range)
ratios_styled_dfs: dict[str, Styler] = ratios_outputter.prepare_styled_output(model_df)

# Write the output to an Excel file, which will have colored cells for deviations outside the
# range. The file will have two worksheets worksheets, one with summary and one with full
# comparison (mirroring the dict produced in the previous step).
ratios_outputter.to_excel('comparison.xlsx', results=ratios_styled_dfs)
