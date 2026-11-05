"""
    RegrEval

Lightweight regression model evaluation metrics for Julia.
"""
module RegrEval

using Statistics: mean

export METRIC_NAMES, evaluate

include("validation.jl")
include("evaluation.jl")

end
