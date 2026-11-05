# Benchmark validation

This directory provides simple datasets for checking that the Python
`regreval` and Julia `RegrEval` packages produce the same regression evaluation
results.

The benchmark is intended to validate metric calculations. It is not intended
to compare model prediction performance.

## Files

- `data.xlsx`: Input data for all benchmark cases.
- `manual_validation.xlsx`: Independent validation using Excel formulas.
- `python_validation.ipynb`: Python calculations using `regreval`.
- `julia_validation.ipynb`: Julia calculations using `RegrEval`.

## Benchmark cases

| Sheet | Description | Rows |
|---|---|---:|
| `case 1` | Perfect prediction | 8 |
| `case 2` | Mixed error components | 8 |
| `case 3` | Mean bias, dominated by ECT | 8 |
| `case 4` | Scale bias, dominated by ER | 8 |
| `case 5` | Disturbance error, dominated by ED | 8 |
| `case 6` | Pairwise missing-value removal | 8 raw (6 valid) |
| `case 7` | Constant prediction and undefined correlation | 8 |
| `case 8` | Perfect negative correlation | 8 |
| `case 9` | Linear model fitted to the Iris data | 150 |

Cases 1–8 contain `obs` and `pred` columns and are designed to check specific
formulas and edge cases.

Case 9 uses the Iris dataset from the UCI Machine Learning Repository (CC BY 4.0). Data source: <https://archive.ics.uci.edu/dataset/53/iris>.

Reference: Fisher, R. A. (1936). The use of multiple measurements in taxonomic problems. *Annals of Eugenics*, 7, 179–188.

Case 9 contains `sepal_length` and `sepal_width`. Each notebook independently fits the following model using all 150 observations:

```text
sepal_width = intercept + slope * sepal_length
```

Python uses `numpy.linalg.lstsq`, while Julia uses the `LinearAlgebra` standard library. The fitted sepal widths are then evaluated
against the observed sepal widths.

Case 9 is included only to validate metric calculations on real data. The same data are used to fit and evaluate the model, so it is not intended to assess prediction performance on a separate test dataset.

Because case 9 evaluates an ordinary least-squares model on its fitting data, ECT and ER are theoretically zero, so ED accounts for all MSPE in theory. Tiny nonzero values may appear because of floating-point arithmetic.

## Comparing results

Python and Julia should produce the same results as the independent Excel
calculations, apart from normal floating-point differences in the final decimal
places. In particular:

- percentages may differ from exact 0 or 100 by a very small amount;
- theoretically zero components may appear as very small values, such as
  `1e-30`;
- mathematically undefined results are represented as `NaN` in Python and
  Julia, and as `#N/A` in Excel.
