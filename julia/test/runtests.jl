using RegrEval
using Statistics: mean
using Test

@testset "RegrEval.evaluate" begin
    @testset "result fields and types" begin
        result = RegrEval.evaluate([1, 2, 3], [1.1, 1.9, 3.2])

        @test isdefined(RegrEval, :evaluate)
        @test :evaluate ∉ names(RegrEval)
        @test propertynames(result) == METRIC_NAMES
        @test length(result) == 16
        @test result.n isa Int
        for name in METRIC_NAMES[2:end]
            @test getproperty(result, name) isa Float64
        end
    end

    @testset "direct reference calculation" begin
        observed = [1.0, 2.0, 4.0, 5.0]
        predicted = [1.2, 1.8, 3.5, 5.5]
        result = RegrEval.evaluate(observed, predicted)

        errors = predicted .- observed
        mean_observed = mean(observed)
        mean_predicted = mean(predicted)
        centered_observed = observed .- mean_observed
        centered_predicted = predicted .- mean_predicted
        variance_observed = mean(centered_observed .^ 2)
        variance_predicted = mean(centered_predicted .^ 2)
        covariance = mean(centered_observed .* centered_predicted)
        sd_observed = sqrt(variance_observed)
        sd_predicted = sqrt(variance_predicted)
        pearson = covariance / (sd_observed * sd_predicted)

        mspe = mean(errors .^ 2)
        rmspe = sqrt(mspe)
        ect = (mean_predicted - mean_observed)^2
        er = (sd_predicted - pearson * sd_observed)^2
        ed = (1.0 - pearson^2) * variance_observed
        denominator = (
            variance_observed +
            variance_predicted +
            (mean_observed - mean_predicted)^2
        )
        slope = covariance / variance_observed

        expected = (
            n = 4,
            RMSPE_pct = rmspe / mean_observed * 100.0,
            RMSPE = rmspe,
            MAE = mean(abs.(errors)),
            MSPE = mspe,
            ECT = ect,
            ER = er,
            ED = ed,
            ECT_pct = ect / mspe * 100.0,
            ER_pct = er / mspe * 100.0,
            ED_pct = ed / mspe * 100.0,
            CCC = 2.0 * covariance / denominator,
            Pearson_r = pearson,
            Cb = 2.0 * sd_observed * sd_predicted / denominator,
            slope = slope,
            intercept = mean_predicted - slope * mean_observed,
        )

        @test result.n == expected.n
        for name in METRIC_NAMES[2:end]
            @test isapprox(
                getproperty(result, name),
                getproperty(expected, name);
                rtol=1e-12,
                atol=1e-14,
            )
        end
        @test result.ECT + result.ER + result.ED ≈ result.MSPE
        @test result.ECT_pct + result.ER_pct + result.ED_pct ≈ 100.0
    end

    @testset "perfect prediction" begin
        result = RegrEval.evaluate([1, 2, 3, 4], [1, 2, 3, 4])

        @test result.n == 4
        for name in (:RMSPE_pct, :RMSPE, :MAE, :MSPE, :ECT)
            @test getproperty(result, name) == 0.0
        end
        for name in (:ER, :ED)
            @test isapprox(getproperty(result, name), 0.0; rtol=0.0, atol=1e-14)
        end
        for name in (:ECT_pct, :ER_pct, :ED_pct)
            @test isnan(getproperty(result, name))
        end
        @test result.CCC ≈ 1.0
        @test result.Pearson_r ≈ 1.0
        @test result.Cb ≈ 1.0
        @test result.slope ≈ 1.0
        @test result.intercept ≈ 0.0
    end

    @testset "perfect constant prediction" begin
        result = RegrEval.evaluate([2.0, 2.0, 2.0], [2.0, 2.0, 2.0])
        for name in (:RMSPE_pct, :RMSPE, :MAE, :MSPE, :ECT)
            @test getproperty(result, name) == 0.0
        end
        for name in (
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
            @test isnan(getproperty(result, name))
        end
    end

    @testset "pairwise missing-value removal" begin
        with_missing = RegrEval.evaluate(
            [1.0, 2.0, NaN, 4.0, 5.0],
            [1.1, NaN, 3.0, 3.8, 5.2],
        )
        cleaned = RegrEval.evaluate([1.0, 4.0, 5.0], [1.1, 3.8, 5.2])
        @test isequal(with_missing, cleaned)

        with_missing_value = RegrEval.evaluate(
            [1.0, missing, 3.0],
            [1.0, 2.0, 3.1],
        )
        cleaned_missing_value = RegrEval.evaluate([1.0, 3.0], [1.0, 3.1])
        @test isequal(with_missing_value, cleaned_missing_value)
    end

    @testset "invalid inputs" begin
        @test_throws ArgumentError RegrEval.evaluate([1, 2, NaN], [1, 2])
        @test_throws ArgumentError RegrEval.evaluate([1 2; 3 4], [1 2; 3 4])
        @test_throws ArgumentError RegrEval.evaluate([1, 2, Inf], [1, 2, 3])
        @test_throws ArgumentError RegrEval.evaluate([1, NaN], [1, 2])
        @test_throws ArgumentError RegrEval.evaluate([1, "not numeric"], [1, 2])
        @test_throws ArgumentError RegrEval.evaluate([1 + 0im, 2 + 0im], [1, 2])
    end

    @testset "zero observed mean" begin
        result = RegrEval.evaluate([-1.0, 0.0, 1.0], [-0.8, 0.1, 1.2])
        @test isnan(result.RMSPE_pct)
        @test isfinite(result.RMSPE)
    end

    @testset "constant prediction" begin
        result = RegrEval.evaluate([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])
        @test isnan(result.Pearson_r)
        @test isnan(result.ER)
        @test isnan(result.ED)
        @test result.ECT_pct == 0.0
        @test isnan(result.ER_pct)
        @test isnan(result.ED_pct)
        @test result.CCC == 0.0
        @test result.Cb == 0.0
        @test result.slope ≈ 0.0
        @test result.intercept ≈ 2.0
    end

    @testset "constant observed values" begin
        result = RegrEval.evaluate([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])
        @test isnan(result.Pearson_r)
        @test isnan(result.ER)
        @test isnan(result.ED)
        @test result.ECT_pct == 0.0
        @test isnan(result.ER_pct)
        @test isnan(result.ED_pct)
        @test isnan(result.slope)
        @test isnan(result.intercept)
    end
end
