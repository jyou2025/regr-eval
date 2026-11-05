"""Validate paired inputs and return pairwise-cleaned `Float64` vectors."""
function _prepare_paired_data(observed::AbstractVector, predicted::AbstractVector)
    length(observed) == length(predicted) || throw(ArgumentError(
        "observed and predicted must have the same length; " *
        "got $(length(observed)) and $(length(predicted))"
    ))

    observed_clean = Float64[]
    predicted_clean = Float64[]
    sizehint!(observed_clean, length(observed))
    sizehint!(predicted_clean, length(predicted))

    for (observed_value, predicted_value) in zip(observed, predicted)
        if !ismissing(observed_value) && !(observed_value isa Real)
            throw(ArgumentError("observed and predicted must contain real numeric values"))
        end
        if !ismissing(predicted_value) && !(predicted_value isa Real)
            throw(ArgumentError("observed and predicted must contain real numeric values"))
        end

        if ismissing(observed_value) || ismissing(predicted_value)
            continue
        end

        observed_float = Float64(observed_value)
        predicted_float = Float64(predicted_value)

        if isnan(observed_float) || isnan(predicted_float)
            continue
        end

        if !isfinite(observed_float) || !isfinite(predicted_float)
            throw(ArgumentError("observed and predicted must not contain infinite values"))
        end

        push!(observed_clean, observed_float)
        push!(predicted_clean, predicted_float)
    end

    length(observed_clean) >= 2 || throw(ArgumentError(
        "at least two valid paired observations are required"
    ))

    return observed_clean, predicted_clean
end

function _prepare_paired_data(observed, predicted)
    throw(ArgumentError("observed and predicted must be one-dimensional vectors"))
end
