from iam_validation.criteria import TimeseriesRefCriterion
from iam_validation.targets import CriterionTargetRange
import pyam, pandas as pd

# Load your reference timeseries data for one or more variables
ref_data = pyam.IamDataFrame('./my_reference_data.xlsx')

# Create a reference object that computes the ratio of model results to reference
# data and define allowed target range of +/- 5%.
timeseries_ref = TimeseriesRefCriterion(criterion_name='Reference data ratio comparison',
    reference=ref_data, comparison_function='ratio', broadcast_dims=('model', 'scenario'))
target_range = CriterionTargetRange(criterion=timeseries_ref, target=1.0, range=(0.95, 1.05))

# Load the model data that you want to compare to the reference data
model_df = pyam.IamDataFrame('./my_model_output.xlsx')

# Get a pandas.Series with the ratios of model data relative to reference data, for each data
# point that exists in both the model output and reference data
comparison_ratios: pd.Series = timeseries_ref.get_values(model_df)

# Get a pandas.Series with True/False for what data points are inside the allowed target
# range.
in_range_statuses: pd.Series = target_range.get_in_range(model_df)
