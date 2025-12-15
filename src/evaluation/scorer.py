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
        Score agent results with SEPARATE phenomenon-level and data-level scoring.
        
        Phenomenon-level: Binary pass/fail (pass if ALL P tests pass, score = 1.0, else 0.0)
        Data-level: Binary pass/fail (pass if ALL D tests pass, score = 1.0, else 0.0)
        Overall score: Average of phenomenon and data scores (0.0, 0.5, or 1.0)
        
        Args:
            study: Study object
            agent_results: Results returned by agent
            
        Returns:
            Dictionary with separate phenomenon_result, data_result, and overall_score:
            {
                "phenomenon_result": {
                    "passed": bool,  # True if ALL P tests pass
                    "score": float,  # 1.0 if passed, 0.0 if failed
                    "tests": {...},
                    "total_tests": int,
                    "passed_tests": int
                },
                "data_result": {
                    "passed": bool,  # True if ALL D tests pass
                    "score": float,  # 1.0 if passed, 0.0 if failed
                    "tests": {...},
                    "total_tests": int,
                    "passed_tests": int
                },
                "overall_score": float  # Average of phenomenon and data (0.0, 0.5, or 1.0)
            }
        """
        ground_truth = study.ground_truth
        validation_criteria = ground_truth["validation_criteria"]
        required_tests = validation_criteria["required_tests"]
        
        # Run each validation test
        phenomenon_tests = {}  # Separate P tests
        data_tests = {}        # Separate D tests
        
        phenomenon_score = 0.0
        phenomenon_weight = 0.0
        data_score = 0.0
        data_weight = 0.0
        
        phenomenon_passed_count = 0
        phenomenon_total_count = 0
        
        for test_spec in required_tests:
            test_id = test_spec["test_id"]
            test_type = test_spec["test_type"]
            weight = test_spec.get("weight", 1.0)
            is_critical = test_spec.get("critical", False)
            
            # Run appropriate test based on test_type
            if test_type == "phenomenon_level":
                result = self._run_phenomenon_test(agent_results, ground_truth, test_spec)
                phenomenon_total_count += 1
                if result.get("passed", False):
                    phenomenon_passed_count += 1
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
            if test_type == "phenomenon_level":
                phenomenon_tests[test_id] = test_result
                # For phenomenon: score is binary (1.0 if pass, 0.0 if fail)
                phenomenon_score += (1.0 if passed else 0.0) * weight
                phenomenon_weight += weight
            elif test_type == "data_level":
                data_tests[test_id] = test_result
                data_score += score * weight
                data_weight += weight
            
        # PHENOMENON RESULT: Binary pass/fail
        # Pass = ALL P tests pass (100%)
        phenomenon_passed = (phenomenon_passed_count == phenomenon_total_count and 
                            phenomenon_total_count > 0)
        phenomenon_score_final = 1.0 if phenomenon_passed else 0.0
        
        # DATA RESULT: Binary pass/fail (pass if ALL D tests pass)
        data_total_count = len(data_tests)
        data_passed_count = sum(1 for test in data_tests.values() if test.get("passed", False))
        data_passed = (data_passed_count == data_total_count and data_total_count > 0)
        data_score_final = 1.0 if data_passed else 0.0
        
        # Calculate weighted scores for P and D separately
        total_weighted_p_score = 0.0
        total_p_weight = 0.0
        
        for test in phenomenon_tests.values():
            # Use partial score if available (from 0.0 to 1.0), otherwise binary
            test_score = test.get("score", 1.0 if test.get("passed", False) else 0.0)
            test_weight = test.get("weight", 1.0)
            total_weighted_p_score += test_score * test_weight
            total_p_weight += test_weight
            
        total_weighted_d_score = 0.0
        total_d_weight = 0.0
        
        for test in data_tests.values():
            test_score = test.get("score", 1.0 if test.get("passed", False) else 0.0)
            test_weight = test.get("weight", 1.0)
            total_weighted_d_score += test_score * test_weight
            total_d_weight += test_weight

        # OVERALL SCORE: Weighted average of Phenomenon and Data scores
        # Recommended weighting: Phenomenon (2.0) vs Data (1.0)
        # Reason: Mechanism validity (Phenomenon) is prerequisite for quantitative fidelity (Data)
        
        # Calculate raw scores first (0.0 to 1.0)
        p_raw_score = total_weighted_p_score / total_p_weight if total_p_weight > 0 else 0.0
        d_raw_score = total_weighted_d_score / total_d_weight if total_d_weight > 0 else 0.0
        
        # Apply 3:1 weighting as requested
        overall_score = (p_raw_score * 3.0 + d_raw_score * 1.0) / 4.0
        
        return {
            "study_id": study.id,
            "phenomenon_result": {
                "passed": phenomenon_passed,
                "score": p_raw_score,
                "tests": phenomenon_tests,
                "total_tests": phenomenon_total_count,
                "passed_tests": phenomenon_passed_count,
                "weight": phenomenon_weight
            },
            "data_result": {
                "passed": data_passed,
                "score": d_raw_score,
                "tests": data_tests,
                "total_tests": data_total_count,
                "passed_tests": data_passed_count,
                "weight": data_weight
            },
            "overall_score": overall_score,
            # Legacy fields
            "total_score": overall_score,
            "passed": phenomenon_passed,
            "phenomenon_tests": phenomenon_tests,
            "data_tests": data_tests,
            "phenomenon_score": p_raw_score,
            "data_score": d_raw_score
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
            elif test_name == "proportion_test":
                return self._test_proportion(agent_results, ground_truth, test_spec)
            elif test_name == "independent_t_test":
                return self._test_independent_t(agent_results, ground_truth, test_spec)
            elif test_name == "one_sample_t_test":
                return self._test_one_sample_t(agent_results, ground_truth, test_spec)
            elif test_name == "paired_t_test":
                return self._test_paired_t(agent_results, ground_truth, test_spec)
            elif test_name == "correlation":
                return self._test_correlation(agent_results, ground_truth, test_spec)
            elif test_name == "range_test":
                return self._test_range(agent_results, ground_truth, test_spec)
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
        
        Supports two methods:
        1. TOST equivalence testing (default)
        2. Absolute difference testing (for simpler metrics like FCE magnitude)
        
        Args:
            agent_results: Agent's aggregated results
            ground_truth: Study ground truth
            test_spec: Test specification with data_type and human_baseline
            
        Returns:
            Dict with score, passed status, and test details
        """
        try:
            method = test_spec.get("method", {})
            test_type = method.get("test", "tost")
            
            if test_type == "absolute_difference":
                return self._test_absolute_difference(agent_results, ground_truth, test_spec)
            else:
                # Default to TOST equivalence testing
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
            method = test_spec.get("method", {})
            agent_inf = agent_results.get("inferential_statistics", {})
            
            # Support source_field parameter for custom test locations
            source_field = method.get("source_field")
            if source_field:
                # Read from specified field (e.g., "birth_sequence_effect")
                test_result = agent_inf.get(source_field, {})
                if not test_result:
                    return {"score": 0.0, "passed": False, "details": {"error": f"No test found at field '{source_field}'"}}
            else:
                # Default: read from chi_square_test field
                test_result = agent_inf.get("chi_square_test", {})
                if not test_result:
                    return {"score": 0.0, "passed": False, "details": {"error": "No chi-square test found"}}
            
            agent_p = test_result.get("p_value")
            agent_chi2 = test_result.get("chi_square")
            
            if agent_p is None:
                return {"score": 0.0, "passed": False, "details": {"error": "No p-value found"}}
            
            # Check if significant (p < 0.05)
            threshold = method.get("threshold", 0.05)
            is_significant = agent_p < threshold
            
            # For phenomenon tests, we want significant results (effect is present)
            passed = is_significant
            score = 1.0 if passed else 0.0
            
            details = {
                "agent_chi2": float(agent_chi2) if agent_chi2 is not None else None,
                "agent_p_value": float(agent_p),
                "threshold": float(threshold),
                "is_significant": bool(is_significant),
                "source_field": source_field if source_field else "chi_square_test"
            }
            
            return {"score": float(score), "passed": bool(passed), "details": details}
            
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
            elif ">" in direction:
                # Format: "condition1 > condition2" or "condition1 > other_conditions"
                parts = [p.strip() for p in direction.split(">")]
                if len(parts) == 2:
                    cond1 = parts[0]
                    cond2 = parts[1]
                    expected_direction = "greater"
                else:
                    return {"score": 0.0, "passed": False, "details": {"error": f"Invalid direction format: {direction}"}}
            elif "<" in direction:
                # Format: "condition1 < condition2"
                parts = [p.strip() for p in direction.split("<")]
                if len(parts) == 2:
                    cond1 = parts[0]
                    cond2 = parts[1]
                    expected_direction = "less"
                else:
                    return {"score": 0.0, "passed": False, "details": {"error": f"Invalid direction format: {direction}"}}
            elif "conditions" in method:
                # Legacy format with explicit conditions
                conditions = method["conditions"]
                if len(conditions) != 2:
                    return {"score": 0.0, "passed": False, "details": {"error": "Need exactly 2 conditions"}}
                cond1, cond2 = conditions
                expected_direction = method.get("expected_direction", "greater")
            else:
                return {"score": 0.0, "passed": False, "details": {"error": f"Cannot parse direction: {direction}"}}
            
            # Handle special cases for combined conditions (e.g., "descriptive_norms" or "other_descriptive_norms")
            # Check if we need to compute combined statistics
            if cond1 == "descriptive_norms" or cond1 == "all_descriptive_norms_combined":
                # Combine all descriptive norm conditions
                descriptive_conditions = ["descriptive_norm_guest", "descriptive_norm_room", 
                                         "descriptive_norm_citizen", "descriptive_norm_gender"]
                if "by_condition" in agent_desc:
                    combined_data = self._combine_conditions(agent_desc["by_condition"], descriptive_conditions)
                    data1 = combined_data
                else:
                    return {"score": 0.0, "passed": False, "details": {"error": "Missing by_condition data for combined descriptive norms"}}
            elif cond1 in agent_desc:
                data1 = agent_desc[cond1]
            elif "by_condition" in agent_desc and cond1 in agent_desc["by_condition"]:
                data1 = agent_desc["by_condition"][cond1]
            else:
                return {"score": 0.0, "passed": False, "details": {"error": f"Missing condition data: {cond1}"}}
            
            if cond2 == "other_descriptive_norms":
                # Combine descriptive norm conditions except room
                other_conditions = ["descriptive_norm_guest", "descriptive_norm_citizen", "descriptive_norm_gender"]
                if "by_condition" in agent_desc:
                    combined_data = self._combine_conditions(agent_desc["by_condition"], other_conditions)
                    data2 = combined_data
                else:
                    return {"score": 0.0, "passed": False, "details": {"error": "Missing by_condition data for other descriptive norms"}}
            elif cond2 in agent_desc:
                data2 = agent_desc[cond2]
            elif "by_condition" in agent_desc and cond2 in agent_desc["by_condition"]:
                data2 = agent_desc["by_condition"][cond2]
            else:
                return {"score": 0.0, "passed": False, "details": {"error": f"Missing condition data: {cond2}"}}
            
            # Try multiple possible field names for proportions
            prop1 = (data1.get("proportion_choose_safe") or 
                    data1.get("obedience_rate") or
                    data1.get("towel_reuse_rate") or
                    data1.get("proportion") or
                    data1.get("rate"))
            prop2 = (data2.get("proportion_choose_safe") or 
                    data2.get("obedience_rate") or
                    data2.get("towel_reuse_rate") or
                    data2.get("proportion") or
                    data2.get("rate"))
            
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
                f"{cond1}_proportion": float(prop1),
                f"{cond2}_proportion": float(prop2),
                "direction": direction,
                "expected_direction": expected_direction,
                "correct_direction": bool(passed)
            }
            
            return {"score": float(score), "passed": bool(passed), "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}
    
    def _test_one_sample_t(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """Test if a variable is significantly different from a comparison value."""
        try:
            from scipy import stats
            
            method = test_spec.get("method", {})
            agent_inf = agent_results.get("inferential_statistics", {})
            
            # Support source_field parameter for pre-calculated tests
            source_field = method.get("source_field")
            if source_field:
                test_result = agent_inf.get(source_field, {})
                if not test_result:
                    return {"score": 0.0, "passed": False, "details": {"error": f"No test found at field '{source_field}'"}}
                
                p_value = test_result.get("p_value")
                t_stat = test_result.get("t_statistic")
                
                if p_value is None:
                    return {"score": 0.0, "passed": False, "details": {"error": "No p-value found"}}
                
                # Check significance
                threshold = method.get("threshold", 0.05)
                is_significant = p_value < threshold
                
                # Check direction if specified (e.g. t > 0)
                passed = is_significant
                expected_direction = method.get("expected_direction")
                if expected_direction == "positive" and t_stat is not None:
                    if t_stat <= 0: passed = False
                elif expected_direction == "negative" and t_stat is not None:
                    if t_stat >= 0: passed = False
                
                return {
                    "score": 1.0 if passed else 0.0,
                    "passed": bool(passed),
                    "details": {
                        "t_statistic": float(t_stat) if t_stat is not None else None,
                        "p_value": float(p_value),
                        "threshold": float(threshold),
                        "is_significant": bool(is_significant),
                        "source_field": source_field
                    }
                }

            variable = method.get("variable", "")
            comparison_value = method.get("comparison_value", 0.0)
            alternative = method.get("alternative", "two-sided")
            
            # Extract data based on variable name
            values = []
            if variable == "anchoring_index":
                # Specific extraction logic for anchoring index
                by_question = agent_results.get("by_question", {})
                for q_data in by_question.values():
                    if "anchoring_index" in q_data:
                        values.append(q_data["anchoring_index"])
            else:
                # Generic extraction (not implemented for now)
                pass
            
            if not values:
                return {"score": 0.0, "passed": False, "details": {"error": f"No data found for {variable}"}}
            
            # Perform one-sample t-test
            t_stat, p_value = stats.ttest_1samp(values, popmean=comparison_value, alternative=alternative)
            
            # Check significance (alpha = 0.05)
            is_significant = p_value < 0.05
            
            # Also check direction (for one-sided tests, scipy handles p-value, but check mean)
            mean_val = np.mean(values)
            passed = is_significant
            
            score = 1.0 if passed else 0.0
            
            details = {
                "variable": variable,
                "mean": float(mean_val),
                "n": len(values),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant": bool(is_significant)
            }
            
            return {"score": float(score), "passed": bool(passed), "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}

    def _test_paired_t(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """Test if two paired variables are significantly different."""
        try:
            from scipy import stats
            
            method = test_spec.get("method", {})
            var1_name = method.get("variable_1", "")
            var2_name = method.get("variable_2", "")
            alternative = method.get("alternative", "two-sided")
            
            # Extract paired data
            # Assuming data is in by_question structure for Study 002
            by_question = agent_results.get("by_question", {})
            
            vals1 = []
            vals2 = []
            
            # Support for P2: High vs Low Asymmetry
            # Requires high_anchor_ai and low_anchor_ai fields in question data
            if var1_name == "high_anchor_ai" and var2_name == "low_anchor_ai":
                for q_data in by_question.values():
                    v1 = q_data.get("high_anchor_ai")
                    v2 = q_data.get("low_anchor_ai")
                    
                    if v1 is not None and v2 is not None:
                        vals1.append(v1)
                        vals2.append(v2)
            else:
                # Generic extraction not yet implemented for other pairs
                return {"score": 0.0, "passed": False, "details": {"error": f"Unsupported variable pair: {var1_name}, {var2_name}"}}
            
            if not vals1:
                return {"score": 0.0, "passed": False, "details": {"error": "No data found for paired t-test"}}
            
            # Perform paired t-test
            t_stat, p_value = stats.ttest_rel(vals1, vals2, alternative=alternative)
            
            # Check significance
            is_significant = p_value < 0.05
            
            # Check direction (mean diff)
            mean1 = np.mean(vals1)
            mean2 = np.mean(vals2)
            
            passed = is_significant
            
            details = {
                "variable_1": var1_name,
                "variable_2": var2_name,
                "mean_1": float(mean1),
                "mean_2": float(mean2),
                "n": len(vals1),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant": bool(is_significant)
            }
            
            return {"score": 1.0 if passed else 0.0, "passed": bool(passed), "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}

    def _test_correlation(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """Test correlation between two variables."""
        try:
            from scipy import stats
            
            method = test_spec.get("method", {})
            var1_name = method.get("variable_1", "")
            var2_name = method.get("variable_2", "")
            expected_direction = method.get("expected_direction", "any")
            
            # Extract data from by_question
            by_question = agent_results.get("by_question", {})
            vals1 = []
            vals2 = []
            
            for q_data in by_question.values():
                v1 = None
                v2 = None
                
                # Handle variable mapping
                if var1_name == "anchoring_index":
                    v1 = q_data.get("anchoring_index")
                elif var1_name == "mean_confidence":
                    # Average of high and low confidence
                    h_conf = q_data.get("high_confidence")
                    l_conf = q_data.get("low_confidence")
                    if h_conf is not None and l_conf is not None:
                        v1 = (h_conf + l_conf) / 2
                
                if var2_name == "mean_confidence":
                    h_conf = q_data.get("high_confidence")
                    l_conf = q_data.get("low_confidence")
                    if h_conf is not None and l_conf is not None:
                        v2 = (h_conf + l_conf) / 2
                
                if v1 is not None and v2 is not None:
                    vals1.append(v1)
                    vals2.append(v2)
            
            if len(vals1) < 3:
                return {"score": 0.0, "passed": False, "details": {"error": "Not enough data points for correlation"}}
            
            # Compute correlation
            corr, p_value = stats.pearsonr(vals1, vals2)
            
            # Check significance and direction
            is_significant = p_value < 0.05
            direction_match = True
            
            if expected_direction == "positive":
                direction_match = corr > 0
            elif expected_direction == "negative":
                direction_match = corr < 0
            
            passed = is_significant and direction_match
            score = 1.0 if passed else 0.0
            
            details = {
                "correlation": float(corr),
                "p_value": float(p_value),
                "significant": bool(is_significant),
                "direction_match": bool(direction_match)
            }
            
            return {"score": float(score), "passed": bool(passed), "details": details}
            
        except Exception as e:
            return {"score": 0.0, "passed": False, "details": {"error": str(e)}}
        """
        Combine multiple conditions into a single aggregated statistic.
        
        Args:
            by_condition: Dictionary with condition names as keys
            condition_names: List of condition names to combine
        
        Returns:
            Combined statistics dictionary
        """
        combined_n = 0
        combined_count = 0
        rates = []
        
        for cond_name in condition_names:
            if cond_name in by_condition:
                cond_data = by_condition[cond_name]
                n = cond_data.get("n", 0)
                rate = cond_data.get("towel_reuse_rate") or cond_data.get("obedience_rate") or cond_data.get("proportion_choose_safe") or cond_data.get("rate", 0.0)
                combined_n += n
                combined_count += int(rate * n) if n > 0 else 0
                if n > 0:
                    rates.append(rate)
        
        combined_rate = combined_count / combined_n if combined_n > 0 else 0.0
        
        return {
            "n": combined_n,
            "towel_reuse_rate": combined_rate,
            "rate": combined_rate,
            "proportion": combined_rate
        }
    
    def _test_independent_t(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """
        Run independent samples t-test for continuous data.
        
        Tests whether the mean of one condition is significantly different from another.
        Used for studies with continuous dependent variables (e.g., numerical estimates).
        
        Args:
            agent_results: Agent's aggregated results with descriptive_statistics
            ground_truth: Study ground truth
            test_spec: Test specification with method containing:
                - comparison: e.g., "high_anchor_vs_low_anchor"
                - threshold: significance level (default 0.05)
                - direction: expected direction, e.g., "high > low"
        
        Returns:
            Dict with score, passed status, and test details
        """
        from scipy import stats
        
        try:
            agent_desc = agent_results.get("descriptive_statistics", {})
            agent_inf = agent_results.get("inferential_statistics", {})
            method = test_spec.get("method", {})
            
            # Support source_field parameter for custom test locations (e.g. Study 001 combined tests)
            source_field = method.get("source_field")
            if source_field:
                test_result = agent_inf.get(source_field, {})
                if not test_result:
                    return {"score": 0.0, "passed": False, "details": {"error": f"No test found at field '{source_field}'"}}
                
                p_value = test_result.get("p_value")
                t_stat = test_result.get("t_statistic")
                
                if p_value is None:
                    return {"score": 0.0, "passed": False, "details": {"error": "No p-value found in test result"}}
                
                # Check significance
                threshold = method.get("threshold", 0.05)
                is_significant = p_value < threshold
                
                # Check direction if specified
                # Study 001: We want p < 0.05 (significance of FCE)
                # For Study 001, t-statistic is (Mean_A - Mean_B), so positive t means FCE > 0
                passed = is_significant
                
                # If direction check is needed (e.g. t > 0)
                expected_direction = method.get("expected_direction") # "positive" or "negative"
                if expected_direction == "positive" and t_stat is not None:
                    if t_stat <= 0: passed = False
                elif expected_direction == "negative" and t_stat is not None:
                    if t_stat >= 0: passed = False
                
                return {
                    "score": 1.0 if passed else 0.0,
                    "passed": bool(passed),
                    "details": {
                        "t_statistic": float(t_stat) if t_stat is not None else None,
                        "p_value": float(p_value),
                        "threshold": float(threshold),
                        "is_significant": bool(is_significant),
                        "source_field": source_field
                    }
                }

            # Parse comparison specification
            comparison = method.get("comparison", "")
            if "_vs_" in comparison:
                cond1, cond2 = comparison.split("_vs_")
            else:
                return {"score": 0.0, "passed": False, 
                       "details": {"error": f"Invalid comparison format: {comparison}"}}
            
            # Determine question from test_id (for Study 002 format)
            # Test IDs like "P1", "P2", "P3" correspond to questions
            test_id = test_spec.get("test_id", "")
            question_map = {
                "P1": "washington",
                "P2": "chicago", 
                "P3": "everest"
            }
            question = question_map.get(test_id)
            
            # Try two data formats:
            # Format 1: nested by condition (standard)
            # Format 2: nested by question with flattened conditions (Study 002)
            
            if question and question in agent_desc:
                # Study 002 format: descriptive_statistics[question][mean_high/low, sd_high/low, n_high/low]
                question_data = agent_desc[question]
                
                # Map condition names to field suffixes
                # "high_anchor" or "high" -> "_high"
                # "low_anchor" or "low" -> "_low"
                suffix1 = "_" + cond1.replace("_anchor", "")
                suffix2 = "_" + cond2.replace("_anchor", "")
                
                mean1 = question_data.get(f"mean{suffix1}")
                mean2 = question_data.get(f"mean{suffix2}")
                sd1 = question_data.get(f"sd{suffix1}")
                sd2 = question_data.get(f"sd{suffix2}")
                n1 = question_data.get(f"n{suffix1}")
                n2 = question_data.get(f"n{suffix2}")
                
            elif cond1 in agent_desc and cond2 in agent_desc:
                # Standard format: descriptive_statistics[condition][mean, sd, n]
                # Also support study-specific field names like mean_remarks, sd_remarks
                data1 = agent_desc[cond1]
                data2 = agent_desc[cond2]
                
                # Try multiple possible field names for mean
                # Use explicit None checks to handle 0.0 values correctly
                mean1 = (data1.get("mean") if data1.get("mean") is not None else
                        data1.get("mean_remarks") if data1.get("mean_remarks") is not None else
                        data1.get("mean_estimate") if data1.get("mean_estimate") is not None else
                        data1.get("average"))
                mean2 = (data2.get("mean") if data2.get("mean") is not None else
                        data2.get("mean_remarks") if data2.get("mean_remarks") is not None else
                        data2.get("mean_estimate") if data2.get("mean_estimate") is not None else
                        data2.get("average"))
                
                # Try multiple possible field names for sd
                # Use explicit None checks to handle 0.0 values correctly
                sd1 = (data1.get("sd") if data1.get("sd") is not None else
                      data1.get("std") if data1.get("std") is not None else
                      data1.get("sd_remarks") if data1.get("sd_remarks") is not None else
                      data1.get("std_remarks") if data1.get("std_remarks") is not None else
                      data1.get("standard_deviation"))
                sd2 = (data2.get("sd") if data2.get("sd") is not None else
                      data2.get("std") if data2.get("std") is not None else
                      data2.get("sd_remarks") if data2.get("sd_remarks") is not None else
                      data2.get("std_remarks") if data2.get("std_remarks") is not None else
                      data2.get("standard_deviation"))
                
                n1 = data1.get("n", data1.get("sample_size"))
                n2 = data2.get("n", data2.get("sample_size"))
            else:
                return {"score": 0.0, "passed": False,
                       "details": {"error": f"Missing condition data for {cond1} or {cond2}"}}
            
            
            # Validate all required data present
            if None in [mean1, mean2, sd1, sd2, n1, n2]:
                return {"score": 0.0, "passed": False,
                       "details": {"error": "Missing mean, sd, or n for one or both conditions"}}
            
            # Compute t-statistic and p-value
            # Handle edge case: when both SDs are 0
            if sd1 == 0 and sd2 == 0:
                # Both groups have identical values
                if mean1 == mean2:
                    # No difference at all
                    t_stat = 0.0
                    p_value = 1.0
                    df = n1 + n2 - 2  # Standard df for equal SDs
                else:
                    # Perfect separation: completely significant
                    t_stat = np.inf
                    p_value = 0.0
                    df = n1 + n2 - 2  # Standard df for equal SDs
            else:
                # Using Welch's t-test (does not assume equal variances)
                se1 = sd1 / np.sqrt(n1)
                se2 = sd2 / np.sqrt(n2)
                se_diff = np.sqrt(se1**2 + se2**2)
                
                if se_diff == 0:
                    # Edge case: se_diff is 0 but at least one SD > 0
                    # This shouldn't happen, but handle it
                    if mean1 == mean2:
                        t_stat = 0.0
                        p_value = 1.0
                        df = n1 + n2 - 2
                    else:
                        t_stat = np.inf
                        p_value = 0.0
                        df = n1 + n2 - 2
                else:
                    t_stat = (mean1 - mean2) / se_diff
                    
                    # Degrees of freedom (Welch-Satterthwaite equation)
                    df = ((se1**2 + se2**2)**2) / ((se1**4 / (n1 - 1)) + (se2**4 / (n2 - 1)))
                    
                    # Two-tailed p-value
                    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
            
            # Check significance
            threshold = method.get("threshold", 0.05)
            is_significant = p_value < threshold
            
            # Check direction if specified
            direction = method.get("direction", "")
            correct_direction = True
            
            if direction:
                if ">" in direction:
                    # e.g., "high > low" means mean1 should be > mean2
                    correct_direction = mean1 > mean2
                elif "<" in direction:
                    correct_direction = mean1 < mean2
            
            # Test passes if significant AND direction is correct
            passed = is_significant and correct_direction
            score = 1.0 if passed else 0.0
            
            # Compute Cohen's d for effect size
            pooled_sd = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))
            if pooled_sd == 0:
                # When both SDs are 0, Cohen's d is undefined
                # Use a large value to indicate perfect separation
                cohens_d = np.inf if mean1 != mean2 else 0.0
            else:
                cohens_d = (mean1 - mean2) / pooled_sd if pooled_sd > 0 else 0.0
            
            details = {
                f"{cond1}_mean": float(mean1),
                f"{cond2}_mean": float(mean2),
                f"{cond1}_sd": float(sd1),
                f"{cond2}_sd": float(sd2),
                f"{cond1}_n": int(n1),
                f"{cond2}_n": int(n2),
                "t_statistic": float(t_stat),
                "df": float(df),
                "p_value": float(p_value),
                "cohens_d": float(cohens_d),
                "significant": bool(is_significant),
                "threshold": float(threshold),
                "direction": direction,
                "correct_direction": bool(correct_direction)
            }
            
            return {"score": float(score), "passed": bool(passed), "details": details}
            
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
        # Step 1: Get data type and map to standard type
        raw_data_type = test_spec.get("data_type", "proportion")
        
        if raw_data_type == "anchoring_index":
            data_type = "rating"  # Treat AI as a continuous variable with mean/sd
        elif raw_data_type == "confidence":
            data_type = "rating"  # Treat confidence as rating
        else:
            data_type = raw_data_type
        
        # Step 2: Get standardizer
        standardizer = StandardizerRegistry.get(data_type)
        
        # Step 3: Extract data
        method_spec = test_spec.get("method", {})
        metric = method_spec.get("metric", "proportion_choose_safe")
        condition = method_spec.get("condition")
        
        # Special handling for Study 002 global metrics
        if metric == "overall_anchoring_index":
            # Extract from overall stats or root
            overall = agent_results.get("overall", agent_results)
            # Try to get exact metric, fallback to mean_anchoring_index
            agent_val = overall.get(metric, overall.get("mean_anchoring_index"))
            
            # Calculate SD from indices if available
            indices = overall.get("anchoring_indices", [])
            agent_sd = np.std(indices) if indices else 0.2
            agent_n = len(indices) if indices else 15
            
            agent_data = {"mean": agent_val, "sd": agent_sd, "n": agent_n}
            
        elif metric == "overall_confidence":
            overall = agent_results.get("overall", agent_results)
            agent_val = overall.get(metric, overall.get("mean_confidence"))
            
            # Calculate SD from all confidences if available
            all_confs = overall.get("all_confidences", [])
            agent_sd = np.std(all_confs) if all_confs else 1.0
            agent_n = len(all_confs) if all_confs else 15
            
            agent_data = {"mean": agent_val, "sd": agent_sd, "n": agent_n}
            
        else:
            # Standard logic for other studies
            
            if not condition:
                 # Fallback or error
                 pass 

            # ... (existing logic for standard extraction) ...
            
            # Re-implementing the existing logic inside the else block to handle flow
            agent_desc = agent_results.get("descriptive_statistics", {})
            
            if condition and condition in agent_desc:
                agent_condition_data = agent_desc[condition]
                
                if data_type == "proportion":
                    agent_value = agent_condition_data.get(metric)
                    agent_n = agent_condition_data.get("n", agent_condition_data.get("sample_size", 100))
                    agent_data = {"proportion": agent_value, "n": agent_n}
                elif data_type == "rating":
                    agent_mean = agent_condition_data.get("mean")
                    agent_sd = agent_condition_data.get("sd", agent_condition_data.get("std", 1.0))
                    agent_n = agent_condition_data.get("n", agent_condition_data.get("sample_size", 100))
                    agent_data = {"mean": agent_mean, "sd": agent_sd, "n": agent_n}
                else: # effect_size
                    agent_effect = agent_condition_data.get("effect_size")
                    agent_se = agent_condition_data.get("se", 0.1)
                    agent_data = {"effect_size": agent_effect, "se": agent_se}
            else:
                # If we reached here and didn't match special cases or standard cases
                return {
                    "score": 0.0, 
                    "passed": False, 
                    "details": {"error": f"Could not extract data for {metric} or condition {condition}"}
                }

        # Check for missing data
        if any(v is None for v in agent_data.values()):
             return {
                "score": 0.0,
                "passed": False,
                "details": {"error": "Extracted agent data contains None values", "data": agent_data}
            }
        
        # Get human baseline
        human_baseline = test_spec.get("human_baseline", {}).copy() # Copy to avoid modifying original
        if not human_baseline:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": "No human baseline specified"}
            }
        
        # Ensure 'n' exists in human_baseline for standardizers that need it
        if "n" not in human_baseline:
            # Default sample size from Study 002 if not specified
            human_baseline["n"] = 145
        
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
        
        # Detailed results - ensure all numeric types are JSON serializable
        details = {
            "data_type": data_type,
            "condition": condition,
            "metric": metric,
            "agent_data": {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                          for k, v in agent_data.items()},
            "human_baseline": {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                              for k, v in human_baseline.items()},
            "standardized_d": float(d),
            "se_pooled": float(se_pooled),
            "delta": float(delta),
            "p_tost": float(p_tost),
            "p_upper": float(tost_result["p_upper"]),
            "p_lower": float(tost_result["p_lower"]),
            "interpretation": tost_result["interpretation"],
            "score_formula": f"1 - {p_tost:.4f}"
        }
        
        return {
            "score": float(score),
            "passed": bool(passed),
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
            agent_desc = agent_results.get("descriptive_statistics", {})
            human_baseline = test_spec.get("human_baseline", {})
            
            # Get effect size name from test spec
            effect_size_name = test_spec.get("method", {}).get("metric", "effect_size")
            
            # Extract agent effect size
            agent_effect_size = None
            
            # First try inferential statistics
            for test_name, test_data in agent_inf.items():
                if effect_size_name in test_data:
                    agent_effect_size = test_data[effect_size_name]
                    break
            
            # If not found, try descriptive statistics (for Study 001 FCE metrics)
            if agent_effect_size is None and effect_size_name in agent_desc:
                agent_effect_size = agent_desc[effect_size_name]
            
            if agent_effect_size is None:
                return {"score": 0.0, "passed": False, "details": {"error": f"Agent metric '{effect_size_name}' not found"}}
            
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
            passed = bool(score >= 0.5)
            
            details = {
                "agent_effect_size": float(agent_effect_size),
                "human_effect_size": float(human_effect_size),
                "absolute_difference": float(abs_diff),
                "score_formula": f"max(0, 1 - {abs_diff:.3f}/{max_diff})",
                "match_quality": match_quality,
                "max_diff_threshold": float(max_diff)
            }
            
            return {"score": float(score), "passed": passed, "details": details}
            
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
    ) -> Dict[str, Any]:
        """Test if statistic is within expected range."""
        try:
            statistic_name = test_spec.get("statistic", "")
            method = test_spec.get("method", {})
            min_val = method.get("min", float("-inf"))
            max_val = method.get("max", float("inf"))
            
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
                
                # Check if statistic is directly in the descriptive statistics root
                if statistic_name in agent_desc:
                    value = agent_desc[statistic_name]
                else:
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
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {"error": f"Statistic '{statistic_name}' not found in results"}
                }
            
            # Check range
            in_range = min_val <= value <= max_val
            
            if in_range:
                score = 1.0
            else:
                # Partial credit based on distance
                if value < min_val:
                    distance = min_val - value
                else:
                    distance = value - max_val
                
                range_size = max(max_val - min_val, 0.01)  # Avoid division by zero
                penalty = min(distance / range_size, 1.0)
                score = max(0.0, 1.0 - penalty)
            
            return {
                "score": float(score),
                "passed": bool(in_range),
                "details": {
                    "statistic": statistic_name,
                    "value": float(value),
                    "min": float(min_val),
                    "max": float(max_val),
                    "in_range": bool(in_range)
                }
            }
        
        except Exception as e:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": str(e)}
            }
    
    def _test_proportion(
        self,
        agent_results: Dict,
        ground_truth: Dict,
        test_spec: Dict
    ) -> Dict[str, Any]:
        """
        Test if a minimum proportion of scenarios/items show the expected effect.
        Used for Study 001 to test FCE across multiple scenarios or questionnaire items.
        
        Args:
            agent_results: Agent's aggregated results
            ground_truth: Study ground truth
            test_spec: Test specification with:
                - method.scenarios: List of scenario keys to check (optional, if not provided checks all study_2_ items)
                - method.min_proportion: Minimum proportion required (e.g., 0.75 = 75%)
        
        Returns:
            Dict with score (proportion of scenarios passing), passed status, and details
        """
        try:
            method = test_spec.get("method", {})
            scenarios = method.get("scenarios", [])
            min_proportion = method.get("min_proportion", 0.75)
            
            desc_stats = agent_results.get("descriptive_statistics", {})
            
            # If no scenarios specified, check all study_2_ items (for Study 2 questionnaire)
            if not scenarios:
                # Filter out summary statistics (like study_2_mean_fce) - only include dicts
                scenarios = [k for k in desc_stats.keys() 
                            if k.startswith("study_2_") and isinstance(desc_stats[k], dict)]
            
            if not scenarios:
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {"error": "No scenarios found to test"}
                }
            
            # Count how many scenarios show positive FCE
            passed_scenarios = []
            failed_scenarios = []
            
            for scenario in scenarios:
                scenario_stats = desc_stats.get(scenario, {})
                if not isinstance(scenario_stats, dict):
                    continue  # Skip non-dict entries
                fce_magnitude = scenario_stats.get("fce_magnitude", 0)
                
                # Check if FCE is positive (indicating the phenomenon is present)
                if fce_magnitude > 0:
                    passed_scenarios.append(scenario)
                else:
                    failed_scenarios.append(scenario)
            
            # Calculate proportion
            total = len(scenarios)
            passed = len(passed_scenarios)
            proportion = passed / total if total > 0 else 0.0
            
            # Test passes if proportion meets or exceeds minimum
            test_passed = proportion >= min_proportion
            
            # Score is the actual proportion (0.0 to 1.0)
            score = proportion
            
            return {
                "score": float(score),
                "passed": bool(test_passed),
                "details": {
                    "total_scenarios": total,
                    "passed_scenarios": passed,
                    "failed_scenarios": len(failed_scenarios),
                    "proportion": float(proportion),
                    "min_proportion_required": float(min_proportion),
                    "passed_scenario_list": passed_scenarios,
                    "failed_scenario_list": failed_scenarios
                }
            }
        
        except Exception as e:
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": str(e)}
            }
    
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
