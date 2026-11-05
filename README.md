# regr-eval

A lightweight toolkit for evaluating regression model predictions, developed
for animal science modelers.

This toolkit provides consistent Python and Julia implementations of prediction-error metrics, MSPE decomposition, agreement measures, correlation, and regression diagnostics.

## Implementations

<table>
  <thead>
    <tr>
      <th>Language</th>
      <th>Link</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Python</td>
      <td><a href="python/README.md"><code>regreval</code></a></td>
    </tr>
    <tr>
      <td>Julia</td>
      <td><a href="julia/README.md"><code>RegrEval</code></a></td>
    </tr>
  </tbody>
</table>

## Mathematical definitions

Let $O_i$ and $P_i$ denote the observed and predicted values for pair $i$,
respectively. Let $n$ denote the number of valid pairs after pairwise removal
of missing values.

### Means, variances, and covariance

All moments use divisor $n$:

$$
\bar O = \frac{1}{n}\sum_{i=1}^{n}O_i,
\qquad
\bar P = \frac{1}{n}\sum_{i=1}^{n}P_i,
$$

$$
s_O^2 = \frac{1}{n}\sum_{i=1}^{n}(O_i-\bar O)^2,
\qquad
s_P^2 = \frac{1}{n}\sum_{i=1}^{n}(P_i-\bar P)^2,
$$

and

$$
s_{OP} = \frac{1}{n}\sum_{i=1}^{n}(O_i-\bar O)(P_i-\bar P).
$$

Here, $s_O^2$ is the variance of the observed values, $s_P^2$ is the
variance of the predicted values, and $s_{OP}$ is their covariance. The
subscript $O$ is the uppercase letter O (observed), not the number zero.

The corresponding standard deviations are

$$
s_O=\sqrt{s_O^2},
\qquad
s_P=\sqrt{s_P^2}.
$$

Thus, $s_O$ denotes the standard deviation of the observed values and $s_P$
denotes the standard deviation of the predicted values.

### Pearson correlation

The Pearson correlation coefficient is

$$
r = \frac{s_{OP}}{s_Os_P}.
$$

It is undefined when either variable has zero variance.

### Prediction-error metrics

#### MSPE and MSE

The mean squared prediction error is

$$
\mathrm{MSPE} = \frac{1}{n}\sum_{i=1}^{n}(P_i-O_i)^2.
$$

This is mathematically the same calculation commonly called mean squared
error (MSE). For the same paired observed and predicted values,

$$
\mathrm{MSPE} \equiv \mathrm{MSE}.
$$

The name MSPE is used here to emphasize prediction evaluation; a duplicate
MSE value is therefore not reported.

#### RMSPE and percentage RMSPE

The root mean squared prediction error is

$$
\mathrm{RMSPE} = \sqrt{\mathrm{MSPE}}.
$$

The percentage RMSPE is normalized by the observed mean:

$$
\mathrm{RMSPE}_{\mathrm{pct}} =
\frac{\mathrm{RMSPE}}{\bar O}\times 100.
$$

Percentage RMSPE is undefined when $\bar O=0$.

#### MAE

The mean absolute error is

$$
\mathrm{MAE} = \frac{1}{n}\sum_{i=1}^{n}\lvert P_i-O_i\rvert.
$$

### MSPE decomposition

The Bibby–Toutenburg decomposition is

$$
\mathrm{MSPE} = \mathrm{ECT} + \mathrm{ER} + \mathrm{ED},
$$

where error due to central tendency is

$$
\mathrm{ECT} = (\bar P-\bar O)^2,
$$

error due to regression is

$$
\mathrm{ER} = (s_P-r\,s_O)^2,
$$

and error due to disturbance is

$$
\mathrm{ED} = (1-r^2)s_O^2.
$$

Here, $r$ is the Pearson correlation coefficient defined above. Numerically,
ED may also be calculated using the algebraically equivalent closure expression

$$
\mathrm{ED} = \mathrm{MSPE}-\mathrm{ECT}-\mathrm{ER}
$$

to avoid disagreement caused by floating-point arithmetic or rounded
intermediate quantities.

For each component $X\in\{\mathrm{ECT},\mathrm{ER},\mathrm{ED}\}$, its
percentage contribution is

$$
X_{\mathrm{pct}} = \frac{X}{\mathrm{MSPE}}\times 100.
$$

The component percentages are undefined when $\mathrm{MSPE}=0$, although all
three absolute components are zero for a perfect prediction.

### Lin's concordance correlation coefficient

Lin's concordance correlation coefficient is

$$
\mathrm{CCC} = \rho_c =
\frac{2s_{OP}}
{s_O^2+s_P^2+(\bar O-\bar P)^2}.
$$

It can also be written as

$$
\rho_c = rC_b,
$$

where the bias correction factor is

$$
C_b =
\frac{2s_Os_P}
{s_O^2+s_P^2+(\bar O-\bar P)^2}.
$$

Pearson's $r$ measures precision, while $C_b$ measures departure from the
45-degree line of perfect agreement.

### Regression slope and intercept

The slope and intercept describe the ordinary least-squares line fitted in an
observed-versus-predicted plot, with observed values on the x-axis and predicted
values on the y-axis:

$$
P_i = \mathrm{intercept} + \mathrm{slope}\,O_i.
$$

The coefficients are

$$
\mathrm{slope} = \frac{s_{OP}}{s_O^2},
$$

and

$$
\mathrm{intercept} = \bar P - \mathrm{slope}\,\bar O.
$$

These are fitted-plot coefficients, not coefficients of the original
prediction model. Under perfect agreement, slope is 1 and intercept is 0. Both
are undefined when the observed values have zero variance.

## References

- Bibby, J., and Toutenburg, H. (1977). *Prediction and Improved Estimation in
  Linear Models*.
- Lin, L. I. (1989). A concordance correlation coefficient to evaluate
  reproducibility. *Biometrics*, 45(1), 255–268.
