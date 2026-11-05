"""Names and order of fields returned by [`evaluate`](@ref)."""
const METRIC_NAMES = (
    :n,
    :RMSPE_pct,
    :RMSPE,
    :MAE,
    :MSPE,
    :ECT,
    :ER,
    :ED,
    :ECT_pct,
    :ER_pct,
    :ED_pct,
    :CCC,
    :Pearson_r,
    :Cb,
    :slope,
    :intercept,
)

"""
    evaluate(observed, predicted)

Calculate the standard RegrEval metric set for paired observed and predicted
values.

Both inputs must be one-dimensional vectors of equal length. Pairs containing
`missing` or `NaN` in either input are removed. At least two valid pairs must
remain, and infinite values are rejected. If either input has zero variance,
Pearson r and the ER and ED decomposition components are undefined and returned
as `NaN`.

The result is a `NamedTuple` whose fields follow [`METRIC_NAMES`](@ref).
Calculations are returned without rounding. MSPE uses the same mathematical
formula as MSE; the MSPE name emphasizes prediction evaluation.
"""
function evaluate(observed, predicted)
    observed, predicted = _prepare_paired_data(observed, predicted)

    mean_observed = mean(observed)
    mean_predicted = mean(predicted)

    errors = predicted .- observed
    mspe = mean(errors .* errors)
    rmspe = sqrt(mspe)
    mae = mean(abs.(errors))

    rmspe_pct = if mean_observed == 0.0
        NaN
    else
        rmspe / mean_observed * 100.0
    end

    observed_centered = observed .- mean_observed
    predicted_centered = predicted .- mean_predicted
    variance_observed = mean(observed_centered .* observed_centered)
    variance_predicted = mean(predicted_centered .* predicted_centered)
    covariance = mean(observed_centered .* predicted_centered)

    sd_observed = sqrt(variance_observed)
    sd_predicted = sqrt(variance_predicted)
    sd_product = sd_observed * sd_predicted

    pearson = if sd_product == 0.0
        NaN
    else
        clamp(covariance / sd_product, -1.0, 1.0)
    end

    ccc_denominator = (
        variance_observed +
        variance_predicted +
        (mean_observed - mean_predicted)^2
    )
    if ccc_denominator == 0.0
        ccc = NaN
        cb = NaN
    else
        ccc = 2.0 * covariance / ccc_denominator
        cb = 2.0 * sd_product / ccc_denominator
    end

    ect = (mean_predicted - mean_observed)^2
    if sd_product == 0.0
        er = NaN
        ed = NaN
    else
        er = (sd_predicted - pearson * sd_observed)^2
        ed_formula = (1.0 - pearson^2) * variance_observed

        ed_residual = mspe - ect - er
        tolerance = 64.0 * eps(Float64) * max(
            1.0,
            abs(mspe),
            abs(ect),
            abs(er),
            abs(ed_formula),
        )
        ed = if ed_residual >= -tolerance
            max(0.0, ed_residual)
        else
            max(0.0, ed_formula)
        end
    end

    if mspe == 0.0
        ect_pct = NaN
        er_pct = NaN
        ed_pct = NaN
    else
        ect_pct = ect / mspe * 100.0
        er_pct = er / mspe * 100.0
        ed_pct = ed / mspe * 100.0
    end

    if variance_observed == 0.0
        slope = NaN
        intercept = NaN
    else
        slope = covariance / variance_observed
        intercept = mean_predicted - slope * mean_observed
    end

    return (
        n = length(observed),
        RMSPE_pct = Float64(rmspe_pct),
        RMSPE = Float64(rmspe),
        MAE = Float64(mae),
        MSPE = Float64(mspe),
        ECT = Float64(ect),
        ER = Float64(er),
        ED = Float64(ed),
        ECT_pct = Float64(ect_pct),
        ER_pct = Float64(er_pct),
        ED_pct = Float64(ed_pct),
        CCC = Float64(ccc),
        Pearson_r = Float64(pearson),
        Cb = Float64(cb),
        slope = Float64(slope),
        intercept = Float64(intercept),
    )
end
