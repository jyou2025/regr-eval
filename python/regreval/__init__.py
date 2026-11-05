"""
A lightweight Python package providing a collection of regression model evaluation metrics for animal science modelers.

"""

from .evaluation import EvaluationResult, METRIC_NAMES, evaluate

__all__ = ["EvaluationResult", "METRIC_NAMES", "evaluate"]
__version__ = "0.1.0"
