"""
Study 005 Configuration - Meeus & Raaijmakers Administrative Obedience (1986)

Implementation of administrative obedience paradigm using psychological harm.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study005PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 005 (Administrative Obedience).
    
    Handles condition-specific prompt generation by loading obedience_condition.txt
    or control_condition.txt based on participant's experimental_condition.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with condition-specific scenario.
        
        Args:
            trial_data: Trial information, may include 'participant_profile' 
                       with 'experimental_condition' key
        
        Returns:
            Trial prompt with appropriate condition text
        """
        # Extract experimental condition from participant profile
        participant_profile = trial_data.get('participant_profile', {})
        experimental_condition = participant_profile.get('experimental_condition', 'obedience')
        
        # Add trial tracking fields
        trial_data["experimental_condition"] = experimental_condition
        trial_data["trial_type"] = "obedience_task"
        trial_data["total_remarks"] = 15
        
        if experimental_condition:
            # Load condition-specific material
            condition_file = self.materials_path / f"{experimental_condition}_condition.txt"
            if condition_file.exists():
                with open(condition_file, 'r') as f:
                    condition_text = f.read().strip()
                return condition_text
        
        # Fallback to generic prompt
        return self._build_generic_trial_prompt(trial_data)


@StudyConfigRegistry.register("study_005")
class Study005Config(BaseStudyConfig):
    """
    Meeus & Raaijmakers (1986) Administrative Obedience
    
    Classic demonstration that people obey authority orders to inflict
    psychological harm on others, with 92% obedience rate.
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Study parameters
        self.conditions = ["obedience", "control"]
        self.total_remarks = 15
        
        # Original study results
        self.original_results = {
            "obedience": {
                "n": 24,
                "obedient": 22,
                "obedience_rate": 0.917,
                "mean_remarks": 14.58,
                "sd_remarks": 1.89
            },
            "control": {
                "n": 15,
                "obedient": 0,
                "obedience_rate": 0.0,
                "mean_remarks": 3.2,
                "sd_remarks": 2.1
            }
        }
    
    def get_prompt_builder(self) -> PromptBuilder:
        """
        Return Study 005 specific PromptBuilder.
        
        Returns:
            Study005PromptBuilder instance that handles condition-specific prompts
        """
        return Study005PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles based on original study's recruitment.
        
        Original study (Meeus & Raaijmakers, 1986):
        - N = 39 (24 obedience, 15 control)
        - Dutch adults ages 18-55
        - Mean age ~32.5
        - Recruited via newspaper advertisement
        - Between-subjects design: obedience vs control condition
        
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
        
        # Assign conditions (between-subjects)
        # Original had 24 obedience, 15 control (roughly 62% obedience, 38% control)
        # For balanced design, use 50/50 split
        n_obedience = n_participants // 2
        n_control = n_participants - n_obedience
        
        # Create condition assignments
        condition_assignments = (["obedience"] * n_obedience + 
                                ["control"] * n_control)
        random.shuffle(condition_assignments)
        
        for i in range(n_participants):
            # Original study: Dutch adults ages 18-55, mean ~32.5
            age = int(np.clip(np.random.normal(32.5, 10), 18, 55))
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": "adult_general_population",
                "background": "You are an adult participating in a research study about personnel selection procedures.",
                "experimental_condition": condition_assignments[i],  # Between-subjects assignment
                "design": "between_subjects"
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial for obedience task.
        
        Each participant gets one trial in their assigned condition.
        The trial involves deciding whether to continue or stop at each
        of the 15 stressful remarks.
        
        Args:
            n_trials: Ignored for this study (always 1 trial per participant)
        
        Returns:
            Single trial dictionary
        """
        # This is a between-subjects design with single trial
        # Condition assignment happens at participant level
        return [{
            "trial_number": 1,
            "study_type": "administrative_obedience",
            "trial_type": "obedience_task",
            "scenario": "stress_interview_administration",
            "total_remarks": 15,
            "condition": "assigned_by_participant"  # Set by participant profile
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate obedience results.
        
        Computes:
        1. Obedience rate by condition (proportion completing all 15 remarks)
        2. Mean number of remarks delivered by condition
        3. Statistical tests (chi-square, independent t-test)
        4. Effect sizes
        
        Args:
            raw_results: Raw results from ParticipantPool.run_experiment()
        
        Returns:
            Enhanced results with obedience analysis
        """
        individual_data = raw_results.get("individual_data", [])
        
        if not individual_data:
            return raw_results
        
        # Separate by condition
        obedience_data = []
        control_data = []
        
        for participant in individual_data:
            condition = participant.get("profile", {}).get("experimental_condition", "obedience")
            if condition == "obedience":
                obedience_data.append(participant)
            else:
                control_data.append(participant)
        
        # Analyze obedience rates and remark counts
        obedience_results = self._analyze_condition(obedience_data, "obedience")
        control_results = self._analyze_condition(control_data, "control")
        
        # Statistical tests
        n_obedience = obedience_results["n"]
        n_control = control_results["n"]
        
        if n_obedience == 0 or n_control == 0:
            return raw_results
        
        # Chi-square test for obedience rates
        obedient_obedience = obedience_results["obedient_count"]
        obedient_control = control_results["obedient_count"]
        disobedient_obedience = obedience_results["disobedient_count"]
        disobedient_control = control_results["disobedient_count"]
        
        contingency_table = np.array([
            [obedient_obedience, disobedient_obedience],
            [obedient_control, disobedient_control]
        ])
        
        try:
            chi2, p_value_chi, dof, expected = stats.chi2_contingency(contingency_table)
        except ValueError as e:
            print(f"⚠️  Warning: Chi-square test failed - {e}")
            chi2, p_value_chi, dof = float('nan'), float('nan'), 1
        
        # Independent t-test for mean remarks delivered
        obedience_remarks = obedience_results["remarks_list"]
        control_remarks = control_results["remarks_list"]
        
        if len(obedience_remarks) >= 2 and len(control_remarks) >= 2:
            t_stat, p_value_t = stats.ttest_ind(obedience_remarks, control_remarks)
            
            # Effect size (Cohen's d)
            mean_diff = obedience_results["mean_remarks"] - control_results["mean_remarks"]
            pooled_sd = np.sqrt(
                ((n_obedience - 1) * obedience_results["sd_remarks"]**2 + 
                 (n_control - 1) * control_results["sd_remarks"]**2) / 
                (n_obedience + n_control - 2)
            )
            cohens_d = mean_diff / pooled_sd if pooled_sd > 0 else 0
        else:
            t_stat, p_value_t, cohens_d = float('nan'), float('nan'), float('nan')
        
        # Proportion difference for obedience rates
        prop_diff = obedience_results["obedience_rate"] - control_results["obedience_rate"]
        
        # Build enhanced results
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": {
                "obedience_condition": {
                    "n": n_obedience,
                    "obedient_count": obedient_obedience,
                    "disobedient_count": disobedient_obedience,
                    "obedience_rate": obedience_results["obedience_rate"],
                    "mean_remarks": obedience_results["mean_remarks"],
                    "sd_remarks": obedience_results["sd_remarks"],
                    "interpretation": self._interpret_obedience_rate(
                        obedience_results["obedience_rate"]
                    )
                },
                "control_condition": {
                    "n": n_control,
                    "obedient_count": obedient_control,
                    "disobedient_count": disobedient_control,
                    "obedience_rate": control_results["obedience_rate"],
                    "mean_remarks": control_results["mean_remarks"],
                    "sd_remarks": control_results["sd_remarks"],
                    "interpretation": self._interpret_obedience_rate(
                        control_results["obedience_rate"]
                    )
                },
                "overall": {
                    "total_n": n_obedience + n_control,
                    "proportion_difference": prop_diff,
                    "mean_remarks_difference": mean_diff,
                    "effect_interpretation": self._interpret_effect(prop_diff, p_value_chi)
                }
            },
            "inferential_statistics": {
                "P1_obedience_above_chance": {
                    "test_type": "proportion_test",
                    "null_hypothesis": "obedience_rate = 0.5",
                    "observed_proportion": obedience_results["obedience_rate"],
                    "n": n_obedience,
                    **self._proportion_test(
                        obedient_obedience, n_obedience, p0=0.5, alternative='greater'
                    ),
                    "significant": obedience_results["obedience_rate"] > 0.5 and 
                                  self._proportion_test(
                                      obedient_obedience, n_obedience, p0=0.5, alternative='greater'
                                  )["p_value"] < 0.05,
                    "interpretation": "Obedience rate significantly exceeds chance" if 
                                     obedience_results["obedience_rate"] > 0.5 else 
                                     "Obedience rate does not exceed chance"
                },
                "P2_condition_difference": {
                    "test_type": "chi_square",
                    "chi_square": float(chi2),
                    "df": int(dof),
                    "p_value": float(p_value_chi),
                    "p": float(p_value_chi),
                    "contingency_table": contingency_table.tolist(),
                    "significant": bool(p_value_chi < 0.05),
                    "interpretation": self._interpret_chi_square(p_value_chi)
                },
                "P3_mean_remarks_difference": {
                    "test_type": "independent_t",
                    "t_statistic": float(t_stat),
                    "df": n_obedience + n_control - 2,
                    "p_value": float(p_value_t),
                    "p": float(p_value_t),
                    "cohens_d": float(cohens_d),
                    "mean_difference": float(mean_diff),
                    "significant": bool(p_value_t < 0.05),
                    "interpretation": self._interpret_t_test(p_value_t, cohens_d)
                }
            },
            "obedience_analysis": {
                "exhibits_obedience": obedience_results["obedience_rate"] > 0.7,
                "condition_effect_significant": bool(p_value_chi < 0.05),
                "effect_size_category": self._categorize_effect_size(cohens_d),
                "matches_original_pattern": (
                    obedience_results["obedience_rate"] > 0.8 and
                    control_results["obedience_rate"] < 0.2
                )
            }
        }
        
        return enhanced_results
    
    def _analyze_condition(self, condition_data: List[Dict[str, Any]], 
                          condition_name: str) -> Dict[str, Any]:
        """
        Analyze obedience data for a single condition.
        
        Args:
            condition_data: List of participant data for this condition
            condition_name: "obedience" or "control"
        
        Returns:
            Dictionary with obedience statistics
        """
        n = len(condition_data)
        
        if n == 0:
            return {
                "n": 0,
                "obedient_count": 0,
                "disobedient_count": 0,
                "obedience_rate": 0.0,
                "mean_remarks": 0.0,
                "sd_remarks": 0.0,
                "remarks_list": []
            }
        
        obedient_count = 0
        remarks_counts = []
        
        for participant in condition_data:
            responses = participant.get("responses", [])
            
            # Determine obedience from response
            if responses:
                last_response = responses[-1]
                response_text = last_response.get("response") or last_response.get("response_text", "")
                
                # Parse number of remarks delivered
                remarks_delivered = self._parse_remarks_delivered(str(response_text))
                remarks_counts.append(remarks_delivered)
                
                # Count as obedient if delivered all 15 remarks
                if remarks_delivered == 15:
                    obedient_count += 1
        
        # Compute statistics
        obedience_rate = obedient_count / n if n > 0 else 0
        mean_remarks = np.mean(remarks_counts) if remarks_counts else 0
        sd_remarks = np.std(remarks_counts, ddof=1) if len(remarks_counts) > 1 else 0
        
        return {
            "n": n,
            "obedient_count": obedient_count,
            "disobedient_count": n - obedient_count,
            "obedience_rate": float(obedience_rate),
            "mean_remarks": float(mean_remarks),
            "sd_remarks": float(sd_remarks),
            "remarks_list": remarks_counts
        }
    
    def _parse_remarks_delivered(self, response_text: str) -> int:
        """
        Parse number of remarks delivered from response.
        
        Expected formats:
        1. "Continue" repeated 15 times = 15 remarks
        2. "Stop" at remark N = N-1 remarks delivered
        3. Explicit number: "I delivered 12 remarks"
        4. Binary choice at each step tracked in response
        
        Args:
            response_text: Raw response text
        
        Returns:
            Number of remarks delivered (0-15)
        """
        import re
        
        if not response_text or response_text == "None":
            return 0
        
        text = str(response_text).strip().upper()
        
        # Pattern 1: Count "CONTINUE" occurrences
        continue_count = text.count("CONTINUE")
        if continue_count > 0:
            # Each "Continue" means one more remark delivered
            return min(continue_count, 15)
        
        # Pattern 2: Look for "STOPPED AT REMARK N" or "STOP AT N"
        stop_match = re.search(r'STOP(?:PED)?\s+(?:AT\s+)?(?:REMARK\s+)?(\d+)', text)
        if stop_match:
            stop_number = int(stop_match.group(1))
            # If stopped at remark N, delivered N-1 remarks
            return max(0, stop_number - 1)
        
        # Pattern 3: Explicit count "DELIVERED N REMARKS" or "N REMARKS"
        delivered_match = re.search(r'(?:DELIVERED\s+)?(\d+)\s+REMARKS?', text)
        if delivered_match:
            return min(int(delivered_match.group(1)), 15)
        
        # Pattern 4: Extract any number (assume it's remark count)
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            for num_str in numbers:
                num = int(num_str)
                if 0 <= num <= 15:
                    return num
        
        # Pattern 5: If response is just "STOP", assume stopped immediately
        if text.strip() == "STOP":
            return 0
        
        # Default: assume full obedience if unclear
        # (This is conservative for detecting obedience)
        return 15
    
    def _proportion_test(self, count: int, n: int, p0: float = 0.5, 
                        alternative: str = 'greater') -> Dict[str, float]:
        """
        One-sample proportion test.
        
        Args:
            count: Number of successes
            n: Sample size
            p0: Null hypothesis proportion
            alternative: 'two-sided', 'greater', or 'less'
        
        Returns:
            Dictionary with z_statistic and p_value
        """
        if n == 0:
            return {"z_statistic": float('nan'), "p_value": float('nan')}
        
        p_hat = count / n
        se = np.sqrt(p0 * (1 - p0) / n)
        
        if se == 0:
            return {"z_statistic": float('nan'), "p_value": float('nan')}
        
        z = (p_hat - p0) / se
        
        if alternative == 'greater':
            p_value = 1 - stats.norm.cdf(z)
        elif alternative == 'less':
            p_value = stats.norm.cdf(z)
        else:  # two-sided
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        return {
            "z_statistic": float(z),
            "p_value": float(p_value),
            "p": float(p_value)
        }
    
    def _interpret_obedience_rate(self, rate: float) -> str:
        """Interpret obedience rate strength."""
        if rate >= 0.90:
            return "Very high obedience matching original study (≥90%)"
        elif rate >= 0.70:
            return "High obedience (70-89%)"
        elif rate >= 0.50:
            return "Moderate obedience (50-69%)"
        elif rate >= 0.30:
            return "Low obedience (30-49%)"
        else:
            return "Minimal obedience (<30%)"
    
    def _interpret_effect(self, prop_diff: float, p_value: float) -> str:
        """Interpret the authority effect."""
        if p_value >= 0.05:
            return "No significant authority effect detected"
        
        if prop_diff >= 0.70:
            return "Very strong authority effect matching original study"
        elif prop_diff >= 0.50:
            return "Strong authority effect"
        elif prop_diff >= 0.30:
            return "Moderate authority effect"
        else:
            return "Small but significant authority effect"
    
    def _interpret_chi_square(self, p_value: float) -> str:
        """Interpret chi-square test result."""
        if p_value < 0.001:
            return "Highly significant condition difference (p < 0.001)"
        elif p_value < 0.01:
            return "Very significant condition difference (p < 0.01)"
        elif p_value < 0.05:
            return "Significant condition difference (p < 0.05)"
        else:
            return "No significant condition difference"
    
    def _interpret_t_test(self, p_value: float, cohens_d: float) -> str:
        """Interpret independent t-test result."""
        if p_value >= 0.05:
            return "No significant difference in remarks delivered"
        
        if abs(cohens_d) >= 2.0:
            return "Very large effect size (|d| ≥ 2.0)"
        elif abs(cohens_d) >= 0.8:
            return "Large effect size (|d| ≥ 0.8)"
        elif abs(cohens_d) >= 0.5:
            return "Medium effect size (|d| ≥ 0.5)"
        else:
            return "Small effect size (|d| < 0.5)"
    
    def _categorize_effect_size(self, cohens_d: float) -> str:
        """Categorize Cohen's d effect size."""
        abs_d = abs(cohens_d)
        if abs_d >= 2.0:
            return "very_large"
        elif abs_d >= 0.8:
            return "large"
        elif abs_d >= 0.5:
            return "medium"
        elif abs_d >= 0.2:
            return "small"
        else:
            return "negligible"
