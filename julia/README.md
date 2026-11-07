# RegrEval

RegrEval is a lightweight Julia package providing a collection of regression model evaluation metrics for animal science modelers.

The package calculates prediction-error metrics (RMSPE_pct, RMSPE, MAE, and
MSPE), the Bibby–Toutenburg MSPE decomposition (ECT, ER, ED, and their
percentage contributions), Lin's concordance correlation coefficient (CCC and
Cb), Pearson correlation, and regression slope and intercept through one
function call.

## Installation

```julia
using Pkg
Pkg.add("RegrEval")
```

## Inputs

To avoid conflicts with functions of the same name exported by other Julia
packages, `evaluate` is not exported and is accessed through the `RegrEval`
namespace:

```julia
RegrEval.evaluate(observed, predicted)
```

| Input | Meaning |
|---|---|
| `observed` | Reference or measured values used as the ground truth |
| `predicted` | Model predictions corresponding one-to-one with the observed values |

Both inputs must be one-dimensional `AbstractVector`s of equal length and must
contain real numeric values, `missing`, or `NaN`. Values at the same position
must represent the same observation. Inputs are converted internally to
`Float64` vectors after pairwise removal of missing values.

The argument order matters: `RMSPE_pct` is normalized by the mean of
`observed`, and slope and intercept are obtained by regressing `predicted` on
`observed`.

## Returned values

`RegrEval.evaluate()` returns a `NamedTuple`. The valid-pair count `n` is an `Int`, and
all metric values are `Float64`.

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
| `slope` | Slope of the fitted line in the observed-versus-predicted plot | Predicted unit per observed unit |
| `intercept` | Intercept of the fitted line in the observed-versus-predicted plot | Same as the predicted values |

Here, `slope` and `intercept` are obtained from the fitted ordinary
least-squares line in the observed-versus-predicted plot, with observed values
on the x-axis and predicted values on the y-axis. They are not coefficients
from the original evaluated model.

The `NamedTuple` follows the fixed order stored in `RegrEval.METRIC_NAMES`.
For a positive MSPE, the preferred decomposition is `ECT_pct` and `ER_pct`
near 0% and `ED_pct` near 100%, indicating that the remaining error is random
rather than systematic. However, `ED_pct` must be interpreted together with
the absolute MSPE: a large MSPE can still have `ED_pct` equal to 100%.

If either input has zero variance, `Pearson_r`, `ER`, `ED`, `ER_pct`, and
`ED_pct` are returned as `NaN` because the decomposition formulas depend on an
undefined Pearson correlation. `ECT` remains defined, and `ECT_pct` remains
defined when MSPE is positive. If the observed values have zero variance,
`slope` and `intercept` are also returned as `NaN`.

For a perfect nonconstant prediction, MSPE and all absolute decomposition
components are theoretically zero. For a perfect constant prediction, `ECT`
is zero while `ER` and `ED` are `NaN`. The three component percentages are
`NaN` whenever MSPE is zero.

The complete formulas and references are documented in the
[project README](https://github.com/jyou2025/regr-eval#mathematical-definitions).

## Basic usage

```julia
using RegrEval

observed = [1.0, 2.0, 4.0, 5.0]
predicted = [1.2, 1.8, 3.5, 5.5]

result = RegrEval.evaluate(observed, predicted)

println(result.MSPE)
println(result.CCC)

for name in METRIC_NAMES
    println(name, ": ", getproperty(result, name))
end
```

## Missing values and input validation

Pairs containing `missing` or `NaN` in either input are removed:

```julia
using RegrEval

observed = [1.0, 2.0, missing, 4.0]
predicted = [1.1, missing, 3.0, 3.9]

result = RegrEval.evaluate(observed, predicted)
println(result.n)  # 2
```

At least two valid pairs must remain. Infinite values are rejected, and
calculations are returned without rounding.

## Dependencies and compatibility

`Statistics` from the Julia standard library is the only runtime dependency.
No external packages are required. RegrEval requires Julia 1.10 or newer.


## Project homepage

https://github.com/jyou2025/regr-eval
