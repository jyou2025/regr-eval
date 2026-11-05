import unittest

import numpy as np

from regreval import EvaluationResult, METRIC_NAMES, evaluate


class TestEvaluate(unittest.TestCase):
    def test_result_keys_order_and_value_types(self):
        result = evaluate([1, 2, 3], [1.1, 1.9, 3.2])
        self.assertIsInstance(result, dict)
        self.assertEqual(tuple(result), METRIC_NAMES)
        self.assertEqual(len(result), 16)
        self.assertIsInstance(result["n"], int)
        self.assertTrue(
            all(isinstance(result[name], float) for name in METRIC_NAMES[1:])
        )
        self.assertEqual(
            METRIC_NAMES,
            (
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
            ),
        )

    def test_evaluation_result_declares_all_keys(self):
        self.assertEqual(tuple(EvaluationResult.__annotations__), METRIC_NAMES)

    def test_values_against_direct_reference_calculation(self):
        observed = np.asarray([1.0, 2.0, 4.0, 5.0])
        predicted = np.asarray([1.2, 1.8, 3.5, 5.5])
        result = evaluate(observed, predicted)

        error = predicted - observed
        mean_observed = np.mean(observed)
        mean_predicted = np.mean(predicted)
        centered_observed = observed - mean_observed
        centered_predicted = predicted - mean_predicted
        variance_observed = np.mean(centered_observed**2)
        variance_predicted = np.mean(centered_predicted**2)
        covariance = np.mean(centered_observed * centered_predicted)
        sd_observed = np.sqrt(variance_observed)
        sd_predicted = np.sqrt(variance_predicted)
        pearson = covariance / (sd_observed * sd_predicted)

        mspe = np.mean(error**2)
        rmspe = np.sqrt(mspe)
        ect = (mean_predicted - mean_observed) ** 2
        er = (sd_predicted - pearson * sd_observed) ** 2
        ed = (1.0 - pearson**2) * variance_observed
        denominator = (
            variance_observed
            + variance_predicted
            + (mean_observed - mean_predicted) ** 2
        )
        slope = covariance / variance_observed

        expected = {
            "n": 4,
            "RMSPE_pct": rmspe / mean_observed * 100.0,
            "RMSPE": rmspe,
            "MAE": np.mean(np.abs(error)),
            "MSPE": mspe,
            "ECT": ect,
            "ER": er,
            "ED": ed,
            "ECT_pct": ect / mspe * 100.0,
            "ER_pct": er / mspe * 100.0,
            "ED_pct": ed / mspe * 100.0,
            "CCC": 2.0 * covariance / denominator,
            "Pearson_r": pearson,
            "Cb": 2.0 * sd_observed * sd_predicted / denominator,
            "slope": slope,
            "intercept": mean_predicted - slope * mean_observed,
        }

        self.assertEqual(result["n"], expected["n"])
        for name in METRIC_NAMES[1:]:
            np.testing.assert_allclose(
                result[name], expected[name], rtol=1e-12, atol=1e-14
            )
        self.assertAlmostEqual(result["ECT"] + result["ER"] + result["ED"], mspe)
        self.assertAlmostEqual(
            result["ECT_pct"] + result["ER_pct"] + result["ED_pct"], 100.0
        )

    def test_perfect_prediction(self):
        result = evaluate([1, 2, 3, 4], [1, 2, 3, 4])
        self.assertEqual(result["n"], 4)
        for name in ("RMSPE_pct", "RMSPE", "MAE", "MSPE", "ECT"):
            self.assertEqual(result[name], 0.0)
        np.testing.assert_allclose(
            [result["ER"], result["ED"]], [0.0, 0.0], atol=1e-14
        )
        for name in ("ECT_pct", "ER_pct", "ED_pct"):
            self.assertTrue(np.isnan(result[name]))
        np.testing.assert_allclose(
            [
                result["CCC"],
                result["Pearson_r"],
                result["Cb"],
                result["slope"],
                result["intercept"],
            ],
            [1.0, 1.0, 1.0, 1.0, 0.0],
        )

    def test_perfect_constant_prediction(self):
        result = evaluate([2.0, 2.0, 2.0], [2.0, 2.0, 2.0])
        for name in ("RMSPE_pct", "RMSPE", "MAE", "MSPE", "ECT"):
            self.assertEqual(result[name], 0.0)
        for name in (
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
        ):
            self.assertTrue(np.isnan(result[name]))

    def test_missing_values_are_removed_pairwise(self):
        with_missing = evaluate(
            [1.0, 2.0, np.nan, 4.0, 5.0],
            [1.1, np.nan, 3.0, 3.8, 5.2],
        )
        cleaned = evaluate([1.0, 4.0, 5.0], [1.1, 3.8, 5.2])
        for name in METRIC_NAMES:
            self.assertEqual(with_missing[name], cleaned[name])

    def test_none_is_treated_as_missing(self):
        with_missing = evaluate([1.0, None, 3.0], [1.0, 2.0, 3.1])
        cleaned = evaluate([1.0, 3.0], [1.0, 3.1])
        for name in METRIC_NAMES:
            self.assertEqual(with_missing[name], cleaned[name])

    def test_mismatched_lengths_raise(self):
        with self.assertRaisesRegex(ValueError, "same length"):
            evaluate([1, 2, np.nan], [1, 2])

    def test_non_1d_input_raises(self):
        with self.assertRaisesRegex(ValueError, "one-dimensional"):
            evaluate([[1, 2], [3, 4]], [[1, 2], [3, 4]])

    def test_infinite_input_raises(self):
        with self.assertRaisesRegex(ValueError, "infinite"):
            evaluate([1, 2, np.inf], [1, 2, 3])

    def test_too_few_valid_pairs_raise(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            evaluate([1, np.nan], [1, 2])

    def test_zero_observed_mean_makes_rmspe_percent_nan(self):
        result = evaluate([-1.0, 0.0, 1.0], [-0.8, 0.1, 1.2])
        self.assertTrue(np.isnan(result["RMSPE_pct"]))
        self.assertTrue(np.isfinite(result["RMSPE"]))

    def test_constant_prediction(self):
        result = evaluate([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])
        self.assertTrue(np.isnan(result["Pearson_r"]))
        self.assertTrue(np.isnan(result["ER"]))
        self.assertTrue(np.isnan(result["ED"]))
        self.assertEqual(result["ECT_pct"], 0.0)
        self.assertTrue(np.isnan(result["ER_pct"]))
        self.assertTrue(np.isnan(result["ED_pct"]))
        self.assertEqual(result["CCC"], 0.0)
        self.assertEqual(result["Cb"], 0.0)
        np.testing.assert_allclose(
            [result["slope"], result["intercept"]], [0.0, 2.0]
        )

    def test_constant_observed_makes_regression_undefined(self):
        result = evaluate([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])
        self.assertTrue(np.isnan(result["Pearson_r"]))
        self.assertTrue(np.isnan(result["ER"]))
        self.assertTrue(np.isnan(result["ED"]))
        self.assertEqual(result["ECT_pct"], 0.0)
        self.assertTrue(np.isnan(result["ER_pct"]))
        self.assertTrue(np.isnan(result["ED_pct"]))
        self.assertTrue(np.isnan(result["slope"]))
        self.assertTrue(np.isnan(result["intercept"]))


if __name__ == "__main__":
    unittest.main()
