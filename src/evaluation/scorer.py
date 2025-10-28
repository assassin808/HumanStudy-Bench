"""
Scorer for evaluating agent performance against ground truth.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from src.core.study import Study
from src.evaluation.metrics import MetricsCalculator


class Scorer:
    """Score agent results against ground truth."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize scorer.
        
        Args:
            config: Configuration dictionary with evaluation parameters
        """
        self.config = config or {}
        self.metrics = MetricsCalculator()
        
        # Default thresholds
        self.alpha = self.config.get("significance_threshold", 0.05)
        self.effect_size_tolerance = self.config.get("effect_size_tolerance", 0.5)
        self.descriptive_tolerance = self.config.get("descriptive_tolerance", 0.20)
        self.passing_threshold = self.config.get("passing_threshold", 0.75)
    
    def score_study(self, study: Study, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score agent results for a single study.
        
        Args:
            study: Study object
            agent_results: Results returned by agent
            
        Returns:
            Dictionary with scores and test results
        """
        ground_truth = study.ground_truth
        validation_criteria = ground_truth["validation_criteria"]
        required_tests = validation_criteria["required_tests"]
        test_weights = validation_criteria["scoring"].get("test_weights", {})
        
        # Run each validation test
        test_results = {}
        total_score = 0.0
        total_weight = 0.0
        
        for test_spec in required_tests:
            test_id = test_spec["test_id"]
            test_type = test_spec["type"]
            weight = test_weights.get(test_id, 1.0)
            
            # Run appropriate test
            if test_type == "statistical_significance":
                score = self._test_statistical_significance(
                    agent_results, ground_truth, test_spec
                )
            elif test_type == "direction_test":
                score = self._test_direction(
                    agent_results, ground_truth, test_spec
                )
            elif test_type == "range_test":
                score = self._test_range(
                    agent_results, ground_truth, test_spec
                )
            elif test_type == "similarity_test":
                score = self._test_similarity(
                    agent_results, ground_truth, test_spec
                )
            else:
                score = 0.0  # Unknown test type
            
            test_results[test_id] = {
                "score": score,
                "weight": weight,
                "status": "PASS" if score >= 0.75 else ("PARTIAL" if score > 0 else "FAIL"),
                "description": test_spec.get("description", "")
            }
            
            total_score += score * weight
            total_weight += weight
        
        # Calculate overall score
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        passed = overall_score >= self.passing_threshold
        
        return {
            "study_id": study.id,
            "total_score": overall_score,
            "passed": passed,
            "total_tests": len(required_tests),
            "tests": test_results
        }
    
    def _test_statistical_significance(
        self, 
        agent_results: Dict, 
        ground_truth: Dict,
        test_spec: Dict
    ) -> float:
        """Test if statistical significance matches."""
        try:
            # Extract p-value from agent results
            agent_inf_stats = agent_results.get("inferential_statistics", {})
            
            # Find the relevant test (simplified - uses first matching)
            agent_p = None
            for test_name, test_data in agent_inf_stats.items():
                if "p_value" in test_data or "p" in test_data:
                    agent_p = test_data.get("p_value", test_data.get("p"))
                    break
            
            if agent_p is None:
                return 0.0
            
            # Check if both are significant or both non-significant
            threshold = test_spec.get("threshold", self.alpha)
            agent_sig = agent_p < threshold
            
            # Get original significance
            original_inf_stats = ground_truth["original_results"]["inferential_statistics"]
            original_p = None
            for test_name, test_data in original_inf_stats.items():
                if "p_value" in test_data or "p" in test_data:
                    original_p = test_data.get("p_value", test_data.get("p"))
                    break
            
            if original_p is None:
                return 0.0
            
            original_sig = original_p < threshold
            
            return 1.0 if agent_sig == original_sig else 0.0
        
        except Exception:
            return 0.0
    
    def _test_direction(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> float:
        """Test if effect direction is correct."""
        try:
            agent_desc = agent_results.get("descriptive_statistics", {})
            original_desc = ground_truth["original_results"]["descriptive_statistics"]
            
            # Get first DV for simplification
            if not agent_desc or not original_desc:
                return 0.0
            
            dv_name = list(agent_desc.keys())[0]
            agent_means = agent_desc[dv_name]
            original_means = original_desc[dv_name]
            
            # Get condition names
            conditions = list(original_means.keys())
            
            if len(conditions) < 2:
                return 1.0  # No comparison needed
            
            # Compare rankings
            agent_ranking = sorted(conditions, key=lambda c: agent_means[c]["mean"], reverse=True)
            original_ranking = sorted(conditions, key=lambda c: original_means[c]["mean"], reverse=True)
            
            # Check if top conditions match
            return 1.0 if agent_ranking[0] == original_ranking[0] else 0.0
        
        except Exception:
            return 0.0
    
    def _test_range(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> float:
        """Test if statistic is within expected range."""
        try:
            statistic_name = test_spec.get("statistic", "")
            min_val = test_spec.get("min", float("-inf"))
            max_val = test_spec.get("max", float("inf"))
            
            # Try to find the statistic value
            value = None
            
            # Check inferential statistics first
            agent_inf_stats = agent_results.get("inferential_statistics", {})
            for test_name, test_data in agent_inf_stats.items():
                if statistic_name in test_data:
                    value = test_data[statistic_name]
                    break
                elif "effect_size_value" in test_data and statistic_name in ["effect_size", "cohens_d", "eta_squared"]:
                    value = test_data["effect_size_value"]
                    break
                elif "cohens_d" in test_data and statistic_name == "cohens_d":
                    value = test_data["cohens_d"]
                    break
            
            # If not found, check descriptive statistics
            if value is None:
                agent_desc = agent_results.get("descriptive_statistics", {})
                for dv_name, dv_data in agent_desc.items():
                    # Check if statistic is directly in the DV data
                    if isinstance(dv_data, dict):
                        # Could be nested by condition or direct stats
                        if statistic_name in dv_data:
                            value = dv_data[statistic_name]
                            break
                        # Check in conditions
                        for condition, stats in dv_data.items():
                            if isinstance(stats, dict) and statistic_name in stats:
                                value = stats[statistic_name]
                                break
                    if value is not None:
                        break
            
            if value is None:
                return 0.0
            
            # Check range
            if min_val <= value <= max_val:
                return 1.0
            else:
                # Partial credit based on distance
                if value < min_val:
                    distance = min_val - value
                else:
                    distance = value - max_val
                
                range_size = max(max_val - min_val, 0.01)  # Avoid division by zero
                penalty = min(distance / range_size, 1.0)
                return max(0.0, 1.0 - penalty)
        
        except Exception:
            return 0.0
    
    def _test_similarity(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> float:
        """Test if descriptive statistics are similar."""
        try:
            agent_desc = agent_results.get("descriptive_statistics", {})
            original_desc = ground_truth["original_results"]["descriptive_statistics"]
            
            tolerance = test_spec.get("tolerance", self.descriptive_tolerance)
            
            scores = []
            
            for dv_name, conditions in original_desc.items():
                if dv_name not in agent_desc:
                    continue
                
                for condition, original_stats in conditions.items():
                    if condition not in agent_desc[dv_name]:
                        continue
                    
                    agent_stats = agent_desc[dv_name][condition]
                    
                    # Compare means
                    mean_error = self.metrics.relative_error(
                        agent_stats["mean"],
                        original_stats["mean"]
                    )
                    mean_score = max(0.0, 1.0 - mean_error / tolerance)
                    
                    scores.append(mean_score)
            
            return np.mean(scores) if scores else 0.0
        
        except Exception:
            return 0.0
