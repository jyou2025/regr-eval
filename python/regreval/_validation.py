"""Input validation shared by regression evaluation functions."""

from __future__ import annotations

import numpy as np


def prepare_paired_data(observed, predicted):
    """Return validated one-dimensional float arrays with missing pairs removed."""
    try:
        observed_array = np.asarray(observed)
        predicted_array = np.asarray(predicted)
    except (TypeError, ValueError) as exc:
        raise ValueError("observed and predicted must be numeric one-dimensional data") from exc

    if observed_array.ndim != 1 or predicted_array.ndim != 1:
        raise ValueError("observed and predicted must be one-dimensional")
    if observed_array.size != predicted_array.size:
        raise ValueError(
            "observed and predicted must have the same length; "
            f"got {observed_array.size} and {predicted_array.size}"
        )
    if np.iscomplexobj(observed_array) or np.iscomplexobj(predicted_array):
        raise ValueError("observed and predicted must contain real numbers")

    try:
        observed_array = np.asarray(observed_array, dtype=np.float64)
        predicted_array = np.asarray(predicted_array, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("observed and predicted must contain numeric values") from exc

    keep = ~np.isnan(observed_array) & ~np.isnan(predicted_array)
    observed_array = observed_array[keep]
    predicted_array = predicted_array[keep]

    if observed_array.size < 2:
        raise ValueError("at least two valid paired observations are required")
    if not np.all(np.isfinite(observed_array)) or not np.all(
        np.isfinite(predicted_array)
    ):
        raise ValueError("observed and predicted must not contain infinite values")

    return observed_array, predicted_array
