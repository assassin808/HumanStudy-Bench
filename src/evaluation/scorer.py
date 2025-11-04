"""
Scorer for evaluating agent performance against ground truth.

Uses equivalence testing (TOST) framework for data-level tests.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from src.core.study import Study
from src.evaluation.metrics import MetricsCalculator
from src.evaluation.standardizers import StandardizerRegistry
from src.evaluation.tost import tost_test, GLOBAL_DELTA


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
        Score agent results for a single study using two-tier evaluation.
        
        Args:
            study: Study object
            agent_results: Results returned by agent
            
        Returns:
            Dictionary with scores and test results
        """
        ground_truth = study.ground_truth
        validation_criteria = ground_truth["validation_criteria"]
        required_tests = validation_criteria["required_tests"]
        
        # Run each validation test
        test_results = {}
        phenomenon_tests = {}  # Separate P tests
        data_tests = {}        # Separate D tests
        
        total_score = 0.0
        total_weight = 0.0
        phenomenon_score = 0.0
        phenomenon_weight = 0.0
        data_score = 0.0
        data_weight = 0.0
        all_critical_passed = True
        
        for test_spec in required_tests:
            test_id = test_spec["test_id"]
            test_type = test_spec["test_type"]
            weight = test_spec.get("weight", 1.0)
            is_critical = test_spec.get("critical", False)
            
            # Run appropriate test based on test_type
            if test_type == "phenomenon_level":
                result = self._run_phenomenon_test(agent_results, ground_truth, test_spec)
            elif test_type == "data_level":
                result = self._run_data_level_test(agent_results, ground_truth, test_spec)
            else:
                # Fallback for legacy test types
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
                    score = 0.0
                result = {"score": score, "passed": score >= 0.75}
            
            score = result["score"]
            passed = result.get("passed", False)
            
            test_result = {
                "score": score,
                "weight": weight,
                "critical": is_critical,
                "passed": passed,
                "status": "PASS" if passed else "FAIL",
                "description": test_spec.get("description", ""),
                "details": result.get("details", {})
            }
            
            # Store in appropriate category
            test_results[test_id] = test_result
            if test_type == "phenomenon_level":
                phenomenon_tests[test_id] = test_result
                phenomenon_score += score * weight
                phenomenon_weight += weight
            elif test_type == "data_level":
                data_tests[test_id] = test_result
                data_score += score * weight
                data_weight += weight
            
            # Track critical test failures
            if is_critical and not passed:
                all_critical_passed = False
            
            total_score += score * weight
            total_weight += weight
        
        # Calculate overall score
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        phenomenon_avg = phenomenon_score / phenomenon_weight if phenomenon_weight > 0 else 0.0
        data_avg = data_score / data_weight if data_weight > 0 else 0.0
        
        # Pass requires: (1) all critical tests pass AND (2) overall score >= threshold
        passed = all_critical_passed and (overall_score >= self.passing_threshold)
        
        return {
            "study_id": study.id,
            "total_score": overall_score,
            "passed": passed,
            "all_critical_passed": all_critical_passed,
            "total_tests": len(required_tests),
            "tests": test_results,
            # Separate phenomenon and data results
            "phenomenon_tests": phenomenon_tests,
            "data_tests": data_tests,
            "phenomenon_score": phenomenon_avg,
            "data_score": data_avg,
            # Weight breakdown
            "total_weight": total_weight,
            "phenomenon_weight": phenomenon_weight,
            "data_weight": data_weight
        }
    
    def _run_phenomenon_test(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """
        Run phenomenon-level test (Type 1: tests if psychological phenomenon is present).
        
        Uses original paper's statistical methods (e.g., chi-square, t-test) to verify
        that the agent exhibits the expected cognitive phenomenon.
        
        Args:
            agent_results: Agent's aggregated results
            ground_truth: Study ground truth
            test_spec: Test specification
            
        Returns:
            Dict with score, passed status, and details
        """
        method = test_spec.get("method", {})
        test_name = method.get("test", "")
        
        try:
            if test_name == "chi_square":
                return self._test_chi_square(agent_results, ground_truth, test_spec)
            elif test_name == "proportion_difference":
                return self._test_proportion_difference(agent_results, ground_truth, test_spec)
            else:
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {"error": f"Unknown phenomenon test: {test_name}"}
                }
        except Exception as e:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": str(e)}
            }
    
    def _run_data_level_test(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """
        Run data-level test (Type 2: tests how closely agent data matches human baseline).
        
        Uses TOST (Two One-Sided Tests) equivalence testing framework:
        - Standardizes metrics using study-specific transformations
        - Tests H₁: |d| < δ (equivalence within tolerance)
        - Returns raw p-value (lower = stronger equivalence)
        
        Args:
            agent_results: Agent's aggregated results
            ground_truth: Study ground truth
            test_spec: Test specification with data_type and human_baseline
            
        Returns:
            Dict with score (1 - p_tost), passed status, and TOST details
        """
        try:
            return self._run_equivalence_test(agent_results, ground_truth, test_spec)
        except Exception as e:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": str(e)}
            }
    
    def _test_chi_square(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """Test if chi-square test shows significant effect (matches original paper)."""
        try:
            # Extract chi-square results from agent
            agent_inf = agent_results.get("inferential_statistics", {})
            chi_square_result = agent_inf.get("chi_square_test", {})
            
            if not chi_square_result:
                return {"score": 0.0, "passed": False, "details": {"error": "No chi-square test found"}}
            
            agent_p = chi_square_result.get("p_value")
            agent_chi2 = chi_square_result.get("chi_square")
            
            if agent_p is None:
                return {"score": 0.0, "passed": False, "details": {"error": "No p-value found"}}
            
            # Check if significant (p < 0.05)
            threshold = test_spec.get("method", {}).get("threshold", 0.05)
            is_significant = agent_p < threshold
            
            # For phenomenon tests, we want significant results (effect is present)
            passed = is_significant
            score = 1.0 if passed else 0.0
            
            details = {
                "agent_chi2": agent_chi2,
                "agent_p_value": agent_p,
                "threshold": threshold,
                "is_significant": is_significant
            }
            
            return {"score": score, "passed": passed, "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}
    
    def _test_proportion_difference(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """Test if effect direction matches expected (e.g., positive > negative frame)."""
        try:
            agent_desc = agent_results.get("descriptive_statistics", {})
            method = test_spec.get("method", {})
            
            # Parse direction specification
            direction = method.get("direction", "")
            
            # Handle different direction formats
            if direction == "positive_greater_than_negative":
                cond1, cond2 = "positive_frame", "negative_frame"
                expected_direction = "greater"
            elif direction == "negative_greater_than_positive":
                cond1, cond2 = "negative_frame", "positive_frame"
                expected_direction = "greater"
            elif "conditions" in method:
                # Legacy format with explicit conditions
                conditions = method["conditions"]
                if len(conditions) != 2:
                    return {"score": 0.0, "passed": False, "details": {"error": "Need exactly 2 conditions"}}
                cond1, cond2 = conditions
                expected_direction = method.get("expected_direction", "greater")
            else:
                return {"score": 0.0, "passed": False, "details": {"error": f"Cannot parse direction: {direction}"}}
            
            # Extract proportions for each condition
            if cond1 not in agent_desc or cond2 not in agent_desc:
                return {"score": 0.0, "passed": False, "details": {"error": f"Missing condition data: {cond1} or {cond2}"}}
            
            prop1 = agent_desc[cond1].get("proportion_choose_safe")
            prop2 = agent_desc[cond2].get("proportion_choose_safe")
            
            if prop1 is None or prop2 is None:
                return {"score": 0.0, "passed": False, "details": {"error": "Missing proportion data"}}
            
            # Check expected direction
            if expected_direction == "greater":
                passed = prop1 > prop2
            elif expected_direction == "less":
                passed = prop1 < prop2
            else:
                passed = False
            
            score = 1.0 if passed else 0.0
            
            details = {
                f"{cond1}_proportion": prop1,
                f"{cond2}_proportion": prop2,
                "direction": direction,
                "expected_direction": expected_direction,
                "correct_direction": passed
            }
            
            return {"score": score, "passed": passed, "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}
    
    def _run_equivalence_test(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """
        Run TOST equivalence test for data-level validation.
        
        Workflow:
        1. Determine data type (proportion, rating, effect_size)
        2. Get appropriate standardizer from registry
        3. Extract agent and human data
        4. Compute standardized effect size d
        5. Run TOST with global δ
        6. Return raw p-value and interpretation
        
        Args:
            agent_results: Agent's aggregated results
            ground_truth: Study ground truth
            test_spec: Test specification
            
        Returns:
            Dict with score, passed, and TOST details
        """
        # Step 1: Get data type
        data_type = test_spec.get("data_type", "proportion")
        
        # Step 2: Get standardizer
        standardizer = StandardizerRegistry.get(data_type)
        
        # Step 3: Extract data
        condition = test_spec.get("method", {}).get("condition")
        metric = test_spec.get("method", {}).get("metric", "proportion_choose_safe")
        
        if not condition:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": "No condition specified"}
            }
        
        # Get agent data
        agent_desc = agent_results.get("descriptive_statistics", {})
        if condition not in agent_desc:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": f"Missing condition: {condition}"}
            }
        
        agent_condition_data = agent_desc[condition]
        
        # Extract based on data type
        if data_type == "proportion":
            agent_value = agent_condition_data.get(metric)
            agent_n = agent_condition_data.get("n", agent_condition_data.get("sample_size", 100))
            
            if agent_value is None:
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {"error": f"Missing agent {metric}"}
                }
            
            agent_data = {"proportion": agent_value, "n": agent_n}
            
        elif data_type == "rating":
            agent_mean = agent_condition_data.get("mean")
            agent_sd = agent_condition_data.get("sd", agent_condition_data.get("std", 1.0))
            agent_n = agent_condition_data.get("n", agent_condition_data.get("sample_size", 100))
            
            if agent_mean is None:
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {"error": "Missing agent mean"}
                }
            
            agent_data = {"mean": agent_mean, "sd": agent_sd, "n": agent_n}
            
        else:  # effect_size
            agent_effect = agent_condition_data.get("effect_size")
            agent_se = agent_condition_data.get("se", 0.1)
            
            if agent_effect is None:
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {"error": "Missing agent effect size"}
                }
            
            agent_data = {"effect_size": agent_effect, "se": agent_se}
        
        # Get human baseline
        human_baseline = test_spec.get("human_baseline", {})
        if not human_baseline:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": "No human baseline specified"}
            }
        
        # Step 4: Compute standardized d
        d, details = standardizer.compute(agent_data, human_baseline)
        
        # Extract SE from computation details
        if data_type == "proportion":
            se_pooled = details.get("se_pooled")
            n_agent = agent_data["n"]
            n_human = human_baseline.get("n", 76)
        elif data_type == "rating":
            # For rating data, SE is SD_pooled / sqrt(n)
            sd_pooled = details.get("sd_pooled", 1.0)
            n_agent = agent_data["n"]
            n_human = human_baseline.get("n", 76)
            se_pooled = sd_pooled / np.sqrt((n_agent + n_human) / 2)
        else:  # effect_size
            se_pooled = details.get("se_combined")
            n_agent = 100  # Default for effect sizes
            n_human = 76
        
        # Step 5: Run TOST
        delta = ground_truth.get("delta", GLOBAL_DELTA)
        tost_result = tost_test(d, se_pooled, n_agent, n_human, delta)
        
        # Step 6: Convert p-value to score
        # Lower p-value = stronger equivalence = higher score
        # score = 1 - p_tost (so p=0 → score=1, p=1 → score=0)
        p_tost = tost_result["p_tost"]
        score = max(0.0, 1.0 - p_tost)
        
        # "Passed" if p < 0.05 (can claim equivalence) OR score >= 0.5
        passed = (p_tost < 0.05) or (score >= 0.5)
        
        # Detailed results
        details = {
            "data_type": data_type,
            "condition": condition,
            "metric": metric,
            "agent_data": agent_data,
            "human_baseline": human_baseline,
            "standardized_d": d,
            "se_pooled": se_pooled,
            "delta": delta,
            "p_tost": p_tost,
            "p_upper": tost_result["p_upper"],
            "p_lower": tost_result["p_lower"],
            "interpretation": tost_result["interpretation"],
            "score_formula": f"1 - {p_tost:.4f}"
        }
        
        return {
            "score": score,
            "passed": passed,
            "details": details
        }
    
    def _test_cohens_h(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """
        Test how closely agent proportion matches human baseline using Cohen's h.
        
        Cohen's h quantifies the difference between two proportions:
        h = 2 * (arcsin(√p1) - arcsin(√p2))
        
        Thresholds (Cohen 1988):
        - h < 0.20: excellent match (negligible difference)
        - h < 0.50: good match (small difference)
        - h < 0.80: acceptable match (medium difference)
        - h >= 0.80: poor match (large difference)
        """
        try:
            agent_desc = agent_results.get("descriptive_statistics", {})
            human_baseline = test_spec.get("human_baseline", {})
            
            # Get condition name
            condition = test_spec.get("method", {}).get("condition")
            if not condition:
                return {"score": 0.0, "passed": False, "details": {"error": "No condition specified"}}
            
            # Get agent proportion
            if condition not in agent_desc:
                return {"score": 0.0, "passed": False, "details": {"error": f"Missing condition: {condition}"}}
            
            agent_prop = agent_desc[condition].get("proportion_choose_safe")
            if agent_prop is None:
                return {"score": 0.0, "passed": False, "details": {"error": "Missing agent proportion"}}
            
            # Get human proportion
            human_prop = human_baseline.get("proportion_choose_safe")
            if human_prop is None:
                return {"score": 0.0, "passed": False, "details": {"error": "Missing human proportion"}}
            
            # Calculate Cohen's h
            cohens_h = self._calculate_cohens_h(agent_prop, human_prop)
            
            # Continuous scoring: score decreases linearly with Cohen's h
            # h = 0.0 → score = 1.0 (perfect match)
            # h = 0.8 → score = 0.0 (large difference, fail)
            # Formula: score = max(0, 1 - h/0.8)
            thresholds = test_spec.get("thresholds", {})
            max_h = thresholds.get("acceptable", 0.80)  # Beyond this h, score = 0
            
            score = max(0.0, 1.0 - cohens_h / max_h)
            
            # Interpret quality for reporting
            if cohens_h < 0.20:
                match_quality = "excellent"
            elif cohens_h < 0.50:
                match_quality = "good"
            elif cohens_h < 0.80:
                match_quality = "acceptable"
            else:
                match_quality = "poor"
            
            # Data-level tests: "passed" means score > 0 (some credit given)
            # But practical threshold: score >= 0.5 (h < 0.40)
            passed = score >= 0.5
            
            details = {
                "condition": condition,
                "agent_proportion": agent_prop,
                "human_proportion": human_prop,
                "cohens_h": cohens_h,
                "score_formula": f"max(0, 1 - {cohens_h:.3f}/{max_h})",
                "match_quality": match_quality,
                "max_h_threshold": max_h
            }
            
            return {"score": score, "passed": passed, "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}
    
    def _test_absolute_difference(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """Test if absolute difference in effect sizes matches within tolerance."""
        try:
            agent_inf = agent_results.get("inferential_statistics", {})
            human_baseline = test_spec.get("human_baseline", {})
            
            # Get effect size name from test spec
            effect_size_name = test_spec.get("method", {}).get("metric", "effect_size")
            
            # Extract agent effect size
            agent_effect_size = None
            for test_name, test_data in agent_inf.items():
                if effect_size_name in test_data:
                    agent_effect_size = test_data[effect_size_name]
                    break
            
            if agent_effect_size is None:
                return {"score": 0.0, "passed": False, "details": {"error": "Agent effect size not found"}}
            
            # Get human effect size
            human_effect_size = human_baseline.get(effect_size_name)
            if human_effect_size is None:
                return {"score": 0.0, "passed": False, "details": {"error": "Human effect size not found"}}
            
            # Calculate absolute difference
            abs_diff = abs(agent_effect_size - human_effect_size)
            
            # Continuous scoring: score decreases linearly with absolute difference
            # diff = 0.0 → score = 1.0 (perfect match)
            # diff = 0.3 → score = 0.0 (large difference, fail)
            # Formula: score = max(0, 1 - diff/0.3)
            thresholds = test_spec.get("thresholds", {})
            max_diff = thresholds.get("acceptable", 0.30)  # Beyond this, score = 0
            
            score = max(0.0, 1.0 - abs_diff / max_diff)
            
            # Interpret quality for reporting
            if abs_diff < 0.10:
                match_quality = "excellent"
            elif abs_diff < 0.20:
                match_quality = "good"
            elif abs_diff < 0.30:
                match_quality = "acceptable"
            else:
                match_quality = "poor"
            
            # "Passed" means score > 0 (some credit), practical threshold: score >= 0.5 (diff < 0.15)
            passed = score >= 0.5
            
            details = {
                "agent_effect_size": agent_effect_size,
                "human_effect_size": human_effect_size,
                "absolute_difference": abs_diff,
                "score_formula": f"max(0, 1 - {abs_diff:.3f}/{max_diff})",
                "match_quality": match_quality,
                "max_diff_threshold": max_diff
            }
            
            return {"score": score, "passed": passed, "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}
    
    def _calculate_cohens_h(self, p1: float, p2: float) -> float:
        """
        Calculate Cohen's h for two proportions.
        
        Formula: h = 2 * (arcsin(√p1) - arcsin(√p2))
        
        Args:
            p1: First proportion (0-1)
            p2: Second proportion (0-1)
            
        Returns:
            Cohen's h value (absolute value)
        """
        phi1 = 2 * np.arcsin(np.sqrt(p1))
        phi2 = 2 * np.arcsin(np.sqrt(p2))
        return abs(phi1 - phi2)
    
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
