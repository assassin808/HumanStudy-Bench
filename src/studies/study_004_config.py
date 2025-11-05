"""
Study 004 Configuration - Kahneman & Tversky Representativeness Heuristic (1972)

Implementation of classic representativeness bias problems.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study004PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 004 (Representativeness Heuristic).
    
    Handles problem-specific prompt generation by loading birth_sequence.txt
    or program_choice.txt based on participant's assigned_problem.
    
    Note: Also modifies trial_data to include minimal fields for mock agent compatibility.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with problem-specific scenario.
        
        Args:
            trial_data: Trial information, may include 'participant_profile' 
                       with 'assigned_problem' key. Modified in-place for mock agent.
        
        Returns:
            Trial prompt with appropriate problem text
        """
        # Extract problem assignment from participant profile
        participant_profile = trial_data.get('participant_profile', {})
        assigned_problem = participant_profile.get('assigned_problem', 'birth_sequence')
        
        # Add minimal problem-specific fields for mock agent compatibility
        # (Real LLMs don't need these, they work from the prompt text alone)
        if assigned_problem == "birth_sequence":
            trial_data["trial_type"] = "birth_sequence"
            trial_data["correct_answer"] = "72"
        else:  # program_choice
            trial_data["trial_type"] = "program_choice"
            trial_data["correct_answer"] = "B"
        
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
        self.problems = ["birth_sequence", "program_choice"]
    
    def get_prompt_builder(self) -> PromptBuilder:
        """
        Return Study 004 specific PromptBuilder.
        
        Returns:
            Study004PromptBuilder instance that handles problem-specific prompts
        """
        return Study004PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles based on original study's recruitment.
        
        Original study (Kahneman & Tversky, 1972):
        - N ≈ 1500 total across multiple studies
        - High school students grades 10-12 (ages 15-18)
        - College-preparatory schools in Israel
        - Between-subjects design: different participants for each problem
        - Each participant answered ~24 questions in questionnaire format
        
        Args:
            n_participants: Number of participants to generate
            random_seed: Random seed for reproducibility
        
        Returns:
            List of participant profile dictionaries
        """
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        profiles = []
        
        # Assign problems evenly (between-subjects)
        n_birth_seq = n_participants // 2
        n_program = n_participants - n_birth_seq
        
        # Create problem assignments
        problem_assignments = (["birth_sequence"] * n_birth_seq + 
                              ["program_choice"] * n_program)
        random.shuffle(problem_assignments)
        
        for i in range(n_participants):
            # Original study: high school students ages 15-18
            age = int(np.clip(np.random.normal(16.5, 1.0), 15, 18))
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": "high_school_student",
                "background": "You are a high school student who thinks about probability and statistics.",
                "assigned_problem": problem_assignments[i],  # Between-subjects assignment
                "design": "between_subjects"
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial for representativeness heuristic problems.
        
        Each participant gets one trial in their assigned problem condition.
        Between-subjects design: problem assignment happens at participant level.
        
        Args:
            n_trials: Ignored for this study (always 1 trial per participant)
        
        Returns:
            Single trial dictionary
        """
        # This is a between-subjects design with single trial
        # Problem assignment happens at participant level
        return [{
            "trial_number": 1,
            "study_type": "representativeness_heuristic",
            "trial_type": "main_problem",
            "scenario": "representativeness_judgment",
            "problem": "assigned_by_condition"  # Set by participant profile
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate representativeness heuristic results.
        
        Computes:
        1. Proportion exhibiting representativeness bias per problem
        2. Overall bias rate
        3. Statistical significance tests
        
        Args:
            raw_results: Raw results from ParticipantPool.run_experiment()
        
        Returns:
            Enhanced results with representativeness bias analysis
        """
        individual_data = raw_results.get("individual_data", [])
        
        if not individual_data:
            return raw_results
        
        # Initialize counters
        birth_seq_bias_count = 0
        program_choice_bias_count = 0
        birth_seq_total = 0
        program_choice_total = 0
        
        # Count biased responses per problem
        # Use participant profile to determine problem assignment (between-subjects)
        for participant in individual_data:
            profile = participant.get("profile", {})
            assigned_problem = profile.get("assigned_problem")
            
            if not assigned_problem:
                continue  # Skip if no assignment
            
            responses = participant.get("responses", [])
            for response in responses:
                response_text = response.get("response") or response.get("response_text", "")
                if not response_text or response_text == "None":
                    continue  # Skip empty or None responses
                response_text = str(response_text).strip().upper()
                
                if assigned_problem == "birth_sequence":
                    birth_seq_total += 1
                    # Check if judged BGBBBB as less likely (representativeness bias)
                    if self._shows_birth_sequence_bias(response_text, response.get("response_text", "")):
                        birth_seq_bias_count += 1
                
                elif assigned_problem == "program_choice":
                    program_choice_total += 1
                    # Check if chose Program A (representativeness over correctness)
                    if self._chose_representative_program(response_text, response.get("response_text", "")):
                        program_choice_bias_count += 1
        
        # Calculate proportions
        birth_seq_bias_prop = birth_seq_bias_count / birth_seq_total if birth_seq_total > 0 else 0
        program_choice_bias_prop = program_choice_bias_count / program_choice_total if program_choice_total > 0 else 0
        
        # Statistical tests (one-sample proportion test against chance)
        # H0: proportion = 0.5 (no bias), H1: proportion > 0.5 (bias present)
        
        # Birth sequence test
        if birth_seq_total > 0:
            birth_z, birth_p = self._proportion_test(
                birth_seq_bias_count, birth_seq_total, p0=0.5, alternative='greater'
            )
        else:
            birth_z, birth_p = float('nan'), float('nan')
        
        # Program choice test
        if program_choice_total > 0:
            program_z, program_p = self._proportion_test(
                program_choice_bias_count, program_choice_total, p0=0.5, alternative='greater'
            )
        else:
            program_z, program_p = float('nan'), float('nan')
        
        # Build enhanced results
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": {
                "birth_sequence_problem": {
                    "n": birth_seq_total,
                    "bias_count": birth_seq_bias_count,
                    "proportion_judging_less_likely": birth_seq_bias_prop,
                    "interpretation": self._interpret_bias_level(birth_seq_bias_prop)
                },
                "program_problem": {
                    "n": program_choice_total,
                    "representative_choice_count": program_choice_bias_count,
                    "proportion_choosing_representative": program_choice_bias_prop,
                    "proportion_choosing_correct": 1 - program_choice_bias_prop,
                    "interpretation": self._interpret_bias_level(program_choice_bias_prop)
                },
                "overall": {
                    "total_trials": birth_seq_total + program_choice_total,
                    "mean_bias_rate": (birth_seq_bias_prop + program_choice_bias_prop) / 2,
                    "consistency": "high" if abs(birth_seq_bias_prop - program_choice_bias_prop) < 0.2 else "moderate"
                }
            },
            "inferential_statistics": {
                "birth_sequence_effect": {
                    "test_type": "proportion_test",
                    "z_statistic": float(birth_z),
                    "p_value": float(birth_p),
                    "p": float(birth_p),
                    "significant": bool(birth_p < 0.05),
                    "effect_interpretation": self._interpret_effect(birth_seq_bias_prop, birth_p),
                    "conclusion": "Representativeness bias detected" if birth_p < 0.05 else "No significant bias"
                },
                "program_choice_effect": {
                    "test_type": "proportion_test",
                    "z_statistic": float(program_z),
                    "p_value": float(program_p),
                    "p": float(program_p),
                    "significant": bool(program_p < 0.05),
                    "effect_interpretation": self._interpret_effect(program_choice_bias_prop, program_p),
                    "conclusion": "Representativeness bias detected" if program_p < 0.05 else "No significant bias"
                }
            },
            "representativeness_analysis": {
                "exhibits_bias": bool(birth_p < 0.05 and program_p < 0.05),
                "consistent_across_problems": abs(birth_seq_bias_prop - program_choice_bias_prop) < 0.2,
                "stronger_in": "birth_sequence" if birth_seq_bias_prop > program_choice_bias_prop else "program_choice"
            }
        }
        
        return enhanced_results
    
    def _shows_birth_sequence_bias(self, response: str, response_text: str) -> bool:
        """
        Check if participant shows representativeness bias in birth sequence problem.
        
        Bias = judging BGBBBB as less likely than GBGBBG
        Correct answer: Both sequences are equally likely, so estimate should be 72.
        Any estimate < 72 indicates representativeness bias.
        """
        combined = (response + " " + response_text).upper()
        
        # First check for explicit "equal" statements (correct answer)
        if "EQUAL" in combined or response.strip() == "72":
            return False
        
        # Extract numeric estimate from response
        import re
        numbers = re.findall(r'\b\d+\b', response + " " + response_text)
        
        if numbers:
            # Get the first number as the estimate
            estimate = int(numbers[0])
            # Any estimate < 72 shows representativeness bias
            if estimate < 72:
                return True
        
        # Also check for explicit "less likely" language
        less_likely_indicators = [
            "LESS LIKELY" in combined,
            "LESS PROBABLE" in combined,
            "FEWER" in combined,
            "LOWER" in combined,
            "RARER" in combined,
            "UNCOMMON" in combined
        ]
        
        return any(less_likely_indicators)
    
    def _chose_representative_program(self, response: str, response_text: str) -> bool:
        """
        Check if participant chose based on representativeness (Program A) rather than
        statistical correctness (Program B).
        
        Correct answer: Program B (higher variance makes 55% more likely)
        Representativeness bias: choosing Program A (because 55% is closer to 65%)
        """
        combined = (response + " " + response_text).upper()
        response_stripped = response.strip().upper()
        
        # Look for Program A choice
        chose_a = (
            "PROGRAM A" in combined or 
            "PROGRAMME A" in combined or
            response_stripped == "A" or
            response_stripped.startswith("A")
        )
        
        return chose_a
    
    def _proportion_test(self, count: int, n: int, p0: float = 0.5, 
                        alternative: str = 'two-sided') -> tuple:
        """
        One-sample proportion test.
        
        Args:
            count: Number of successes
            n: Sample size
            p0: Null hypothesis proportion
            alternative: 'two-sided', 'greater', or 'less'
        
        Returns:
            (z_statistic, p_value)
        """
        if n == 0:
            return float('nan'), float('nan')
        
        p_hat = count / n
        se = np.sqrt(p0 * (1 - p0) / n)
        z = (p_hat - p0) / se
        
        if alternative == 'greater':
            p_value = 1 - stats.norm.cdf(z)
        elif alternative == 'less':
            p_value = stats.norm.cdf(z)
        else:  # two-sided
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        return z, p_value
    
    def _interpret_bias_level(self, proportion: float) -> str:
        """Interpret the strength of representativeness bias."""
        if proportion >= 0.80:
            return "Very strong representativeness bias (≥80%)"
        elif proportion >= 0.70:
            return "Strong representativeness bias (70-79%)"
        elif proportion >= 0.60:
            return "Moderate representativeness bias (60-69%)"
        elif proportion >= 0.55:
            return "Weak representativeness bias (55-59%)"
        else:
            return "No clear bias (≤55%)"
    
    def _interpret_effect(self, proportion: float, p_value: float) -> str:
        """Interpret the statistical effect."""
        if p_value >= 0.05:
            return "No significant representativeness bias"
        
        if proportion >= 0.75:
            return "Strong representativeness bias consistent with original study"
        elif proportion >= 0.60:
            return "Moderate representativeness bias"
        else:
            return "Weak but significant representativeness bias"
    
    def get_custom_prompt_context(self, trial: Dict[str, Any], 
                                  participant_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide problem-specific prompt context.
        
        Args:
            trial: Trial data
            participant_profile: Participant profile
        
        Returns:
            Context dict with appropriate problem details
        """
        trial_type = trial.get("trial_type")
        
        if trial_type == "birth_sequence":
            return {
                "problem_type": "birth_sequence",
                "reference_sequence": trial.get("reference_sequence"),
                "reference_frequency": trial.get("reference_frequency"),
                "target_sequence": trial.get("target_sequence"),
                "response_format": "Please provide your numerical estimate or indicate whether it's more likely, less likely, or equally likely."
            }
        
        elif trial_type == "program_choice":
            return {
                "problem_type": "program_choice",
                "program_A_boys": trial.get("program_A_boys_proportion"),
                "program_B_boys": trial.get("program_B_boys_proportion"),
                "observed_boys": trial.get("observed_class_boys_proportion"),
                "response_format": "Please respond with either 'Program A' or 'Program B'."
            }
        
        return {}
