"""
HumanStudyBench: A benchmark for evaluating AI agents on human study replication.
"""

__version__ = "0.1.0"
__author__ = "HumanStudyBench Contributors"

from src.core.benchmark import HumanStudyBench
from src.core.study import Study
from src.agents.base_agent import BaseAgent
from src.evaluation.scorer import Scorer

# Export evaluation thresholds for convenience
STUDY_PASS_THRESHOLD = Study.PASS_THRESHOLD
STUDY_HIGH_QUALITY_THRESHOLD = Study.HIGH_QUALITY_THRESHOLD
STUDY_PERFECT_THRESHOLD = Study.PERFECT_THRESHOLD

BENCHMARK_PASS_THRESHOLD = HumanStudyBench.BENCHMARK_PASS_THRESHOLD
BENCHMARK_MIN_PASS_RATE = HumanStudyBench.MIN_PASS_RATE
BENCHMARK_GOOD_THRESHOLD = HumanStudyBench.GOOD_THRESHOLD
BENCHMARK_EXCELLENT_THRESHOLD = HumanStudyBench.EXCELLENT_THRESHOLD

__all__ = [
    "HumanStudyBench",
    "Study",
    "BaseAgent",
    "Scorer",
    "STUDY_PASS_THRESHOLD",
    "STUDY_HIGH_QUALITY_THRESHOLD",
    "STUDY_PERFECT_THRESHOLD",
    "BENCHMARK_PASS_THRESHOLD",
    "BENCHMARK_MIN_PASS_RATE",
    "BENCHMARK_GOOD_THRESHOLD",
    "BENCHMARK_EXCELLENT_THRESHOLD",
]

