from __future__ import annotations

from typing import TypedDict

import numpy as np

from ._validation import prepare_paired_data

EvaluationResult = TypedDict(
    "EvaluationResult",
    {
        "n": int,
        "RMSPE_pct": float,
        "RMSPE": float,
        "MAE": float,
        "MSPE": float,
        "ECT": float,
        "ER": float,
        "ED": float,
        "ECT_pct": float,
        "ER_pct": float,
        "ED_pct": float,
        "CCC": float,
        "Pearson_r": float,
        "Cb": float,
        "slope": float,
        "intercept": float,
    },
)

METRIC_NAMES = (
    "n",
    "RMSPE_pct",
    "RMSPE",
    "MAE",
    "MSPE",
    "ECT",
    "ER",
    "ED",
    "ECT_pct",
    "ER_pct",
    "ED_pct",
    "CCC",
    "Pearson_r",
    "Cb",
    "slope",
    "intercept",
)


def evaluate(observed, predicted) -> EvaluationResult:
    """Calculate the standard RegrEval metric set.

    Missing values are removed pairwise. Inputs must otherwise be finite,
    one-dimensional, equal-length numeric sequences with at least two valid
    pairs. If either input has zero variance, Pearson r and the ER and ED
    decomposition components are undefined and returned as NaN.

    The returned dictionary follows the order in :data:`METRIC_NAMES`.
    Calculations are not rounded.

    Parameters
    ----------
    observed, predicted : array-like
        Paired observed and predicted values.

    Returns
    -------
    EvaluationResult
        A typed dictionary containing the valid-pair count followed by fifteen
        metrics as Python floats.
    """
    observed, predicted = prepare_paired_data(observed, predicted)

    mean_observed = np.mean(observed)
    mean_predicted = np.mean(predicted)

    errors = predicted - observed
    mspe = np.mean(errors * errors)
    rmspe = np.sqrt(mspe)
    mae = np.mean(np.abs(errors))

    if mean_observed == 0.0:
        rmspe_percent = np.nan
    else:
        rmspe_percent = rmspe / mean_observed * 100.0

    observed_centered = observed - mean_observed
    predicted_centered = predicted - mean_predicted
    variance_observed = np.mean(observed_centered * observed_centered)
    variance_predicted = np.mean(predicted_centered * predicted_centered)
    covariance = np.mean(observed_centered * predicted_centered)

    sd_observed = np.sqrt(variance_observed)
    sd_predicted = np.sqrt(variance_predicted)
    sd_product = sd_observed * sd_predicted

    if sd_product == 0.0:
        pearson = np.nan
    else:
        pearson = covariance / sd_product
        pearson = np.clip(pearson, -1.0, 1.0)

    ccc_denominator = (
        variance_observed
        + variance_predicted
        + (mean_observed - mean_predicted) ** 2
    )
    if ccc_denominator == 0.0:
        ccc = np.nan
        cb = np.nan
    else:
        ccc = 2.0 * covariance / ccc_denominator
        cb = 2.0 * sd_product / ccc_denominator

    ect = (mean_predicted - mean_observed) ** 2
    if sd_product == 0.0:
        er = np.nan
        ed = np.nan
    else:
        er = (sd_predicted - pearson * sd_observed) ** 2
        ed_formula = (1.0 - pearson**2) * variance_observed

        ed_residual = mspe - ect - er
        tolerance = 64.0 * np.finfo(np.float64).eps * max(
            1.0, abs(mspe), abs(ect), abs(er), abs(ed_formula)
        )
        if ed_residual >= -tolerance:
            ed = max(0.0, ed_residual)
        else:
            ed = max(0.0, ed_formula)

    if mspe == 0.0:
        ect_percent = np.nan
        er_percent = np.nan
        ed_percent = np.nan
    else:
        ect_percent = ect / mspe * 100.0
        er_percent = er / mspe * 100.0
        ed_percent = ed / mspe * 100.0

    if variance_observed == 0.0:
        slope = np.nan
        intercept = np.nan
    else:
        slope = covariance / variance_observed
        intercept = mean_predicted - slope * mean_observed

    return {
        "n": int(observed.size),
        "RMSPE_pct": float(rmspe_percent),
        "RMSPE": float(rmspe),
        "MAE": float(mae),
        "MSPE": float(mspe),
        "ECT": float(ect),
        "ER": float(er),
        "ED": float(ed),
        "ECT_pct": float(ect_percent),
        "ER_pct": float(er_percent),
        "ED_pct": float(ed_percent),
        "CCC": float(ccc),
        "Pearson_r": float(pearson),
        "Cb": float(cb),
        "slope": float(slope),
        "intercept": float(intercept),
    }
    
