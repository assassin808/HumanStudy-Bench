"""
Study 003 Configuration - Tversky & Kahneman Framing Effect (1981)

Implementation of multiple decision problems from the original paper demonstrating framing effects,
certainty effects, and psychological accounting.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study003PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 003 (Framing Effect & others).
    
    Handles condition-specific prompt generation by loading the appropriate material file
    based on participant's condition (e.g., problem_01.txt, problem_08.txt).
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with condition-specific scenario.
        
        Args:
            trial_data: Trial information, may include 'participant_profile' 
                       with 'condition' key
        
        Returns:
            Trial prompt with appropriate text
        """
        # Extract condition from participant profile
        participant_profile = trial_data.get('participant_profile', {})
        condition = participant_profile.get('condition')
        
        if condition:
            # Load condition-specific material
            
            file_map = {
                "problem_01": "problem_01.txt",
                "problem_02": "problem_02.txt",
                "problem_03": "problem_03.txt",
                "problem_04": "problem_04.txt",
                "problem_05": "problem_05.txt",
                "problem_06": "problem_06.txt",
                "problem_07": "problem_07.txt",
                "problem_08": "problem_08.txt",
                "problem_09": "problem_09.txt",
                "problem_10_1": "problem_10_1.txt",
                "problem_10_2": "problem_10_2.txt"
            }
            
            filename = file_map.get(condition, f"{condition}.txt")
            frame_file = self.materials_path / filename
            
            if frame_file.exists():
                with open(frame_file, 'r') as f:
                    frame_text = f.read().strip()
                return frame_text
        
        # Fallback to generic prompt
        return self._build_generic_trial_prompt(trial_data)



@StudyConfigRegistry.register("study_003")
class Study003Config(BaseStudyConfig):
    """
    Tversky & Kahneman (1981) - The Framing of Decisions and the Psychology of Choice
    
    Replicates multiple problems from the paper:
    - Problem 1 & 2: Asian Disease (Framing Effect)
    - Problem 3 & 4: Framing of Acts
    - Problem 5, 6, 7: Certainty & Pseudocertainty Effects
    - Problem 8 & 9: Psychological Accounting (Theater Ticket)
    - Problem 10: Psychological Accounting (Calculator)
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # List of all conditions
        self.conditions = [
            "problem_01", "problem_02", 
            "problem_03", "problem_04",
            "problem_05", "problem_06", "problem_07",
            "problem_08", "problem_09",
            "problem_10_1", "problem_10_2"
        ]
        
        # Sample sizes from original paper (approximate total N=1360)
        self.condition_ns = {
            "problem_01": 152, "problem_02": 155,
            "problem_03": 150, "problem_04": 86,
            "problem_05": 77,  "problem_06": 85, "problem_07": 81,
            "problem_08": 183, "problem_09": 200,
            "problem_10_1": 93, "problem_10_2": 88
        }
    
    
    def get_prompt_builder(self) -> PromptBuilder:
        """Return Study 003 specific PromptBuilder."""
        return Study003PromptBuilder(self.study_path)

    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles assigned to specific conditions.
        """
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        profiles = []
        
        # Determine N for each condition
        # If n_participants is small (e.g. for testing), distribute evenly
        # If n_participants matches total N, try to match original proportions
        
        total_original_n = sum(self.condition_ns.values())
        
        # Create list of conditions to assign
        assigned_conditions = []
        
        # Calculate how many participants per condition
        for cond, original_n in self.condition_ns.items():
            # Proportional allocation
            count = int(round(n_participants * (original_n / total_original_n)))
            assigned_conditions.extend([cond] * count)
            
        # Adjust length if rounding caused mismatch
        while len(assigned_conditions) < n_participants:
            assigned_conditions.append(random.choice(self.conditions))
        while len(assigned_conditions) > n_participants:
            assigned_conditions.pop()
            
        random.shuffle(assigned_conditions)
        
        for i in range(n_participants):
            # Profile generation logic
            is_faculty = np.random.random() < 0.3
            if is_faculty:
                age = int(np.clip(np.random.normal(45, 8), 30, 65))
                education = "university_faculty"
                background = "You are a university faculty member who regularly makes decisions involving statistical reasoning and risk assessment."
            else:
                age = int(np.clip(np.random.normal(21, 2), 18, 25))
                education = "university_student"
                background = "You are a university student who considers different perspectives when making decisions."
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": education,
                "background": background,
                "condition": assigned_conditions[i]
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial. Condition is determined by participant profile.
        """
        return [{
            "trial_number": 1,
            "study_type": "framing_effect",
            "trial_type": "main_choice",
            "scenario": "decision_problem",
            "frame": "assigned_by_condition"
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate results for all problems (1-10).
        """
        individual_data = raw_results.get("individual_data", [])
        if not individual_data:
            return raw_results
        
        # Group participants by condition
        by_condition = {cond: [] for cond in self.conditions}
        
        for participant in individual_data:
            cond = participant.get("profile", {}).get("condition")
            if cond in by_condition:
                by_condition[cond].append(participant)
        
        # Calculate stats for each condition
        descriptive_stats = {}
        
        for cond, participants in by_condition.items():
            n = len(participants)
            if n == 0:
                continue
                
            choices = self._count_choices(participants)
            
            # Calculate relevant proportions based on condition
            stats_entry = {
                "n": n,
                "counts": choices
            }
            
            # Add specific metrics expected by Scorer
            if cond == "problem_01":
                stats_entry["proportion_A"] = choices.get("A", 0) / n
                stats_entry["proportion_choose_safe"] = stats_entry["proportion_A"] # Alias
                
            elif cond == "problem_02":
                stats_entry["proportion_C"] = choices.get("C", 0) / n # Safe option (loss)
                stats_entry["proportion_D"] = choices.get("D", 0) / n # Risky option
                stats_entry["proportion_choose_safe"] = stats_entry["proportion_C"]
                
            elif cond == "problem_05":
                stats_entry["proportion_A"] = choices.get("A", 0) / n
                stats_entry["proportion_choose_safe"] = stats_entry["proportion_A"]
                
            elif cond == "problem_07":
                stats_entry["proportion_E"] = choices.get("E", 0) / n
                stats_entry["proportion_choose_safe"] = stats_entry["proportion_E"]
                
            elif cond in ["problem_08", "problem_09", "problem_10_1", "problem_10_2"]:
                stats_entry["proportion_Yes"] = choices.get("YES", 0) / n
                stats_entry["proportion_choose_safe"] = stats_entry["proportion_Yes"] # Map Yes to "safe" generic slot
            
            descriptive_stats[cond] = stats_entry

        # Inferential Statistics (Comparisons)
        inferential_stats = {}
        
        # P1: Problem 1 vs 2 (Framing Effect)
        if "problem_01" in descriptive_stats and "problem_02" in descriptive_stats:
            p1_stats = descriptive_stats["problem_01"]
            p2_stats = descriptive_stats["problem_02"]
            
            # Compare Risk Averse choices (A vs C)
            # Note: In Prob 1, A is safe. In Prob 2, C is safe.
            # We compare proportion of SAFE choices.
            
            count_safe_1 = p1_stats["counts"].get("A", 0)
            n1 = p1_stats["n"]
            count_safe_2 = p2_stats["counts"].get("C", 0)
            n2 = p2_stats["n"]
            
            chi2, p = self._run_chi_square(count_safe_1, n1, count_safe_2, n2)
            inferential_stats["chi_square_test"] = {"chi_square": chi2, "p_value": p} # Main effect for compatibility
            inferential_stats["framing_effect_test"] = {"chi_square": chi2, "p_value": p}
            
            # Framing effect size
            descriptive_stats["framing_effect_size"] = (count_safe_1/n1) - (count_safe_2/n2)

        # P2: Problem 5 vs 7 (Certainty Effect)
        if "problem_05" in descriptive_stats and "problem_07" in descriptive_stats:
            # Compare Option A (Safe) vs Option E (Probabilistic)
            # Hypothesis: A is chosen more than E due to certainty premium
            count_A = descriptive_stats["problem_05"]["counts"].get("A", 0)
            n5 = descriptive_stats["problem_05"]["n"]
            count_E = descriptive_stats["problem_07"]["counts"].get("E", 0)
            n7 = descriptive_stats["problem_07"]["n"]
            
            chi2, p = self._run_chi_square(count_A, n5, count_E, n7)
            inferential_stats["certainty_effect_test"] = {"chi_square": chi2, "p_value": p}

        # P3: Problem 8 vs 9 (Lost Ticket)
        if "problem_08" in descriptive_stats and "problem_09" in descriptive_stats:
            # Compare Yes responses
            count_Y8 = descriptive_stats["problem_08"]["counts"].get("YES", 0)
            n8 = descriptive_stats["problem_08"]["n"]
            count_Y9 = descriptive_stats["problem_09"]["counts"].get("YES", 0)
            n9 = descriptive_stats["problem_09"]["n"]
            
            chi2, p = self._run_chi_square(count_Y8, n8, count_Y9, n9)
            inferential_stats["ticket_accounting_test"] = {"chi_square": chi2, "p_value": p}

        # P4: Problem 10_1 vs 10_2 (Calculator)
        if "problem_10_1" in descriptive_stats and "problem_10_2" in descriptive_stats:
            # Compare Yes responses
            count_Y1 = descriptive_stats["problem_10_1"]["counts"].get("YES", 0)
            n1 = descriptive_stats["problem_10_1"]["n"]
            count_Y2 = descriptive_stats["problem_10_2"]["counts"].get("YES", 0)
            n2 = descriptive_stats["problem_10_2"]["n"]
            
            chi2, p = self._run_chi_square(count_Y1, n1, count_Y2, n2)
            inferential_stats["calculator_accounting_test"] = {"chi_square": chi2, "p_value": p}

        enhanced_results = {
            **raw_results,
            "descriptive_statistics": descriptive_stats,
            "inferential_statistics": inferential_stats
        }
        
        return enhanced_results
    
    def _count_choices(self, participant_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count choices flexibly (A/B/C/D/E/F/Yes/No)."""
        counts = {}
        for p in participant_data:
            responses = p.get("responses", [])
            if responses:
                resp = responses[-1].get("response", "?").upper()
                # Normalize A/B/C... to standard keys
                if resp in ["PROGRAM A", "OPTION A", "A"]: key = "A"
                elif resp in ["PROGRAM B", "OPTION B", "B"]: key = "B"
                elif resp in ["PROGRAM C", "OPTION C", "C"]: key = "C"
                elif resp in ["PROGRAM D", "OPTION D", "D"]: key = "D"
                elif resp in ["OPTION E", "E"]: key = "E"
                elif resp in ["OPTION F", "F"]: key = "F"
                elif resp in ["YES", "Y"]: key = "YES"
                elif resp in ["NO", "N"]: key = "NO"
                else: key = "OTHER"
                
                counts[key] = counts.get(key, 0) + 1
        return counts

    def _run_chi_square(self, count1, n1, count2, n2):
        """Helper for 2x2 Chi-Square Test."""
        if n1 == 0 or n2 == 0:
            return 0.0, 1.0
        
        table = np.array([
            [count1, n1 - count1],
            [count2, n2 - count2]
        ])
        try:
            chi2, p, _, _ = stats.chi2_contingency(table)
            return chi2, p
        except:
            return 0.0, 1.0
