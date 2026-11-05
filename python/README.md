# regreval

regreval is a lightweight Python package providing a collection of regression model evaluation metrics for animal science modelers.

`regreval` calculates prediction-error metrics (RMSPE_pct, RMSPE, MAE, and
MSPE), the Bibby–Toutenburg MSPE decomposition (ECT, ER, ED, and their
percentage contributions), Lin's concordance correlation coefficient (CCC and
Cb), Pearson correlation, and regression slope and intercept through one
function call.

## Installation

```bash
pip install regreval
```

## Inputs

The function signature is:

```python
regreval.evaluate(observed, predicted)
```

| Input | Meaning |
|---|---|
| `observed` | Reference or measured values used as the ground truth |
| `predicted` | Model predictions corresponding one-to-one with the observed values |

Both inputs may be one-dimensional Python lists, tuples, NumPy arrays, or
other compatible one-dimensional numeric sequences. They must have the same
length, and values at the same position must represent the same observation.
The observed and predicted values should describe the same quantity in the
same measurement unit.

Inputs are converted internally to NumPy `float64` arrays. The order of the
two arguments matters: `RMSPE_pct` is normalized by the mean of `observed`, and
the reported slope and intercept are obtained by regressing `predicted` on
`observed`.

## Returned values

`evaluate()` returns an insertion-ordered typed dictionary. `n` is a Python
integer and all metric values are Python floats.

| Field | Meaning | Unit |
|---|---|---|
| `n` | Number of valid observed–predicted pairs after pairwise removal of missing values | Count |
| `RMSPE_pct` | Root mean squared prediction error relative to the observed mean | % |
| `RMSPE` | Root mean squared prediction error | Same as the observed values |
| `MAE` | Mean absolute error | Same as the observed values |
| `MSPE` | Mean squared prediction error; numerically equivalent to MSE | Squared unit of the observed values |
| `ECT` | MSPE attributed to error in central tendency | Squared unit of the observed values |
| `ER` | MSPE attributed to error due to regression | Squared unit of the observed values |
| `ED` | MSPE attributed to random disturbance | Squared unit of the observed values |
| `ECT_pct` | Percentage of MSPE attributed to central tendency | % |
| `ER_pct` | Percentage of MSPE attributed to regression | % |
| `ED_pct` | Percentage of MSPE attributed to disturbance | % |
| `CCC` | Lin's concordance correlation coefficient | Unitless |
| `Pearson_r` | Pearson correlation coefficient | Unitless |
| `Cb` | Bias correction factor in Lin's CCC | Unitless |
| `slope` | Slope of the fitted regression line in the observed-versus-predicted plot | Predicted unit per observed unit; unitless when units are identical |
| `intercept` | Intercept of the fitted regression line in the observed-versus-predicted plot | Same as the predicted values |

Here, `slope` and `intercept` are obtained from the fitted ordinary
least-squares line in the observed-versus-predicted plot, with observed values
on the x-axis and predicted values on the y-axis. They are not coefficients
from the original evaluated model.

The dictionary follows the fixed order stored in `regreval.METRIC_NAMES`.
For a positive MSPE, the preferred decomposition is `ECT_pct` and `ER_pct`
near 0% and `ED_pct` near 100%, indicating that the remaining error is random
rather than systematic. However, `ED_pct` must be interpreted together with
the absolute MSPE: a large MSPE can still have `ED_pct` equal to 100%.

If either input has zero variance, `Pearson_r`, `ER`, `ED`, `ER_pct`, and
`ED_pct` are returned as `NaN` because the decomposition formulas depend on an
undefined Pearson correlation. `ECT` remains defined, and `ECT_pct` remains
defined when MSPE is positive.

For a perfect nonconstant prediction, `MSPE` and all absolute decomposition
components are zero. For a perfect constant prediction, `ECT` is zero while
`ER` and `ED` are `NaN`. The three component percentages are `NaN` whenever
MSPE is zero.

The complete formulas and references are documented in the [project README](https://github.com/jyou2025/regr-eval#mathematical-definitions).

## Basic usage

```python
import regreval as rge

observed = [1.0, 2.0, 4.0, 5.0]
predicted = [1.2, 1.8, 3.5, 5.5]

result = rge.evaluate(observed, predicted)

print(result["MSPE"])
print(result["CCC"])

for name, value in result.items():
    print(f"{name}: {value}")
```

The complete field order can be inspected with:

```python
print(rge.METRIC_NAMES)
```

## Missing values and input validation

- Inputs must be one-dimensional numeric sequences of equal length.
- A pair is removed when either its observed or predicted value is missing.
- `n` reports the number of valid pairs remaining after pairwise removal.
- At least two valid pairs must remain.
- Infinite values are rejected rather than treated as missing.
- Calculations are returned without rounding.

For example, only the first and fourth pairs are retained here:

```python
import numpy as np
import regreval as rge

observed = [1.0, 2.0, np.nan, 4.0]
predicted = [1.1, np.nan, 3.0, 3.9]

result = rge.evaluate(observed, predicted)
print(result["n"])  # 2
```

## Multiple models and tabular output

Each result dictionary can be used as one table row. If pandas is already
installed in the user's environment:

```python
import pandas as pd
import regreval as rge

# Replace these values with predictions from your models.
observed = [1.0, 2.0, 4.0, 5.0] 
predicted_a = [1.2, 1.8, 3.5, 5.5]
predicted_b = [1.1, 2.0, 3.8, 5.2]

predictions = {
    "Model A": predicted_a,
    "Model B": predicted_b,
}

rows = [
    {"model": name, **rge.evaluate(observed, predicted)}
    for name, predicted in predictions.items()
]

results_table = pd.DataFrame(rows).set_index("model")
```

Pandas is not a dependency of `regreval`. Results can also be exported with
the Python standard library's `csv.DictWriter`.

## Dependencies and compatibility

NumPy is the sole runtime dependency. The package requires NumPy 1.20 or newer.


## Project Homepage

https://github.com/jyou2025/regr-eval
