"""
Study 004 Configuration - Kahneman & Tversky Representativeness Heuristic (1972)

Implementation of classic representativeness bias problems.
"""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import numpy as np
import random
import re
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study004PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 004 (Representativeness Heuristic).
    
    Handles problem-specific prompt generation by loading corresponding material files.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with problem-specific scenario.
        
        Args:
            trial_data: Trial information, may include 'participant_profile' 
                       with 'assigned_problem' key.
        
        Returns:
            Trial prompt with appropriate problem text
        """
        # Extract problem assignment from participant profile
        participant_profile = trial_data.get('participant_profile', {})
        assigned_problem = participant_profile.get('assigned_problem', 'birth_sequence')
        
        # Set problem-specific metadata
        trial_data["trial_type"] = assigned_problem
        
        # Load problem-specific material for prompt
        problem_file = self.materials_path / f"{assigned_problem}.txt"
        if problem_file.exists():
            with open(problem_file, 'r') as f:
                problem_text = f.read().strip()
            return problem_text
        
        # Fallback
        return self._build_generic_trial_prompt(trial_data)


@StudyConfigRegistry.register("study_004")
class Study004Config(BaseStudyConfig):
    """
    Kahneman & Tversky (1972) Representativeness Heuristic
    
    Classic demonstration that people judge probability based on
    representativeness rather than statistical principles.
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Study parameters
        self.problems = [
            "birth_sequence", 
            "program_choice",
            "marbles_distribution",
            "hospital_problem",
            "word_length",
            "height_check",
            "posterior_chips",
            "posterior_height_1",
            "posterior_height_6"
        ]
    
    def get_prompt_builder(self) -> PromptBuilder:
        return Study004PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        profiles = []
        
        # Assign problems evenly (between-subjects)
        n_problems = len(self.problems)
        base_n = n_participants // n_problems
        remainder = n_participants % n_problems
        
        problem_assignments = []
        for problem in self.problems:
            count = base_n + (1 if remainder > 0 else 0)
            problem_assignments.extend([problem] * count)
            remainder -= 1
            
        random.shuffle(problem_assignments)
        
        for i in range(n_participants):
            # Original study: high school students ages 15-18
            age = int(np.clip(np.random.normal(16.5, 1.0), 15, 18))
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": "high_school_student",
                "background": "You are a high school student who thinks about probability and statistics.",
                "assigned_problem": problem_assignments[i],
                "design": "between_subjects"
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        return [{
            "trial_number": 1,
            "study_type": "representativeness_heuristic",
            "trial_type": "main_problem",
            "scenario": "representativeness_judgment",
            "problem": "assigned_by_condition"
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate representativeness heuristic results.
        """
        individual_data = raw_results.get("individual_data", [])
        
        if not individual_data:
            return raw_results
        
        # Initialize counters
        problem_stats = {p: {"total": 0, "bias_count": 0, "responses": []} for p in self.problems}
        
        for participant in individual_data:
            profile = participant.get("profile", {})
            assigned_problem = profile.get("assigned_problem")
            
            if not assigned_problem or assigned_problem not in problem_stats:
                continue
            
            responses = participant.get("responses", [])
            for response in responses:
                raw_text = response.get("response") or response.get("response_text", "")
                if not raw_text or str(raw_text) == "None":
                    continue
                
                cleaned_text = self._clean_response(str(raw_text))
                problem_stats[assigned_problem]["total"] += 1
                problem_stats[assigned_problem]["responses"].append(cleaned_text)
                
                if self._check_bias(assigned_problem, cleaned_text):
                    problem_stats[assigned_problem]["bias_count"] += 1

        # Calculate statistics
        descriptive_stats = {}
        inferential_stats = {}
        bias_flags = []
        
        for problem, stats_dict in problem_stats.items():
            total = stats_dict["total"]
            bias_count = stats_dict["bias_count"]
            prop = bias_count / total if total > 0 else 0
            
            descriptive_stats[problem] = {
                "n": total,
                "bias_count": bias_count,
                "bias_proportion": prop,
                "interpretation": self._interpret_bias_level(prop)
            }
            
            if total > 0:
                # Skip proportion test for posterior_height comparison group
                if not problem.startswith("posterior_height"):
                    z, p = self._proportion_test(bias_count, total, p0=0.5, alternative='greater')
                    is_significant = p < 0.05
                    bias_flags.append(is_significant)
                    
                inferential_stats[f"{problem}_effect"] = {
                    "test_type": "proportion_test",
                    "z_statistic": float(z),
                    "p_value": float(p),
                    "significant": bool(is_significant),
                    "conclusion": "Bias detected" if is_significant else "No significant bias"
                }
            else:
                inferential_stats[f"{problem}_effect"] = {"error": "No data"}
        
        # Special Comparison: Posterior Height (1 vs 6)
        self._analyze_posterior_height(problem_stats, inferential_stats)
        
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": descriptive_stats,
            "inferential_statistics": inferential_stats,
            "overall_analysis": {
                "bias_detected_in_count": sum(bias_flags),
                "total_tested_conditions": len(bias_flags),
                "consistency": "High" if len(bias_flags) > 0 and sum(bias_flags)/len(bias_flags) > 0.7 else "Moderate"
            }
        }
        
        return enhanced_results

    def _clean_response(self, response: str) -> str:
        """Normalize response text."""
        # Remove "Answer:" prefix if present
        response = re.sub(r'^answer:\s*', '', response, flags=re.IGNORECASE)
        return response.strip().upper()

    def _check_bias(self, problem: str, response: str) -> bool:
        """
        Check if normalized response shows representativeness bias.
        
        Strategies:
        - Birth Sequence: < 72
        - Program Choice: "Program A" or starts with "A"
        - Marbles: "Type I"
        - Hospital/Word/Height: "Same"
        - Posterior Chips: < 0.90 (underestimation)
        """
        if problem == "birth_sequence":
            return self._shows_birth_sequence_bias(response)
            
        bias_checkers: Dict[str, Callable[[str], bool]] = {
            "program_choice": lambda r: "PROGRAM A" in r or r.strip() == "A",
            "marbles_distribution": lambda r: "TYPE I" in r or "TYPE 1" in r or r.strip() == "A",  # A = Type I (bias)
            "hospital_problem": lambda r: "SAME" in r or "ABOUT THE SAME" in r or r.strip() == "C",  # C = same (bias)
            "word_length": lambda r: "SAME" in r or "ABOUT THE SAME" in r or r.strip() == "C",  # C = same (bias)
            "height_check": lambda r: "SAME" in r or "ABOUT THE SAME" in r or r.strip() == "C",  # C = same (bias)
            "posterior_chips": self._check_posterior_chips,
            "posterior_height_1": lambda r: False, # Handled in group analysis
            "posterior_height_6": lambda r: False  # Handled in group analysis
        }
        
        checker = bias_checkers.get(problem)
        return checker(response) if checker else False

    def _analyze_posterior_height(self, problem_stats, inferential_stats):
        """Compare posterior estimates for N=1 vs N=6."""
        resp_1 = self._extract_numbers(problem_stats["posterior_height_1"]["responses"])
        resp_6 = self._extract_numbers(problem_stats["posterior_height_6"]["responses"])
        
        if resp_1 and resp_6:
            mean_1 = float(np.mean(resp_1))
            mean_6 = float(np.mean(resp_6))
            # Hypothesis: Mean(1) > Mean(6) (Representativeness effect)
            # Even though N=6 provides stronger evidence, people rely on the representativeness 
            # of the single mean, and might even judge the single case as more likely 
            # because it's a "perfect match" (5'10").
            t_stat, t_p = stats.ttest_ind(resp_1, resp_6, alternative='greater')
            
            inferential_stats["posterior_height_comparison"] = {
                "mean_odds_1": float(mean_1),
                "mean_odds_6": float(mean_6),
                "prediction": "Mean 1 > Mean 6 (Representativeness)",
                "t_statistic": float(t_stat),
                "p_value": float(t_p),
                "significant": bool(t_p < 0.05),
                "conclusion": "Single case judged more likely than sample" if t_p < 0.05 else "No significant difference"
            }

    def _check_posterior_chips(self, response: str) -> bool:
        """Check if posterior probability is underestimated."""
        nums = self._extract_numbers([response])
        if nums:
            est = nums[0]
            if est > 1: est /= 100.0
            # Correct is ~0.998. Bias is often around 0.7-0.8.
            return est < 0.90
        return False

    def _shows_birth_sequence_bias(self, response: str) -> bool:
        if "EQUAL" in response or response == "72": return False
        nums = self._extract_numbers([response])
        if nums and nums[0] < 72: return True
        return any(x in response for x in ["LESS", "FEWER", "LOWER"])

    def _extract_numbers(self, responses: List[str]) -> List[float]:
        nums = []
        for r in responses:
            # Look for number, possibly with decimal
            found = re.findall(r"[-+]?\d*\.\d+|\d+", r)
            if found:
                try:
                    val = float(found[0])
                    # Handle odds like "3:1" -> 3.0 logic if needed, but simple regex usually grabs first number
                    nums.append(val)
                except ValueError:
                    pass
        return nums

    def _proportion_test(self, count: int, n: int, p0: float = 0.5, alternative: str = 'two-sided') -> tuple:
        if n == 0: return float('nan'), float('nan')
        p_hat = count / n
        se = np.sqrt(p0 * (1 - p0) / n)
        z = (p_hat - p0) / se
        if alternative == 'greater': p_value = 1 - stats.norm.cdf(z)
        elif alternative == 'less': p_value = stats.norm.cdf(z)
        else: p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        return z, p_value

    def _interpret_bias_level(self, proportion: float) -> str:
        if proportion >= 0.80: return "Very strong bias (≥80%)"
        elif proportion >= 0.60: return "Moderate bias (60-79%)"
        else: return "Weak/No clear bias (<60%)"
