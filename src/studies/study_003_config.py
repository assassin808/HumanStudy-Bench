"""
Study 003 Configuration - Tversky & Kahneman Framing Effect (1981)

Implementation of the Asian Disease Problem demonstrating framing effects.
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
    Custom PromptBuilder for Study 003 (Framing Effect).
    
    Handles frame-specific prompt generation by loading positive_frame.txt
    or negative_frame.txt based on participant's framing_condition.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with frame-specific scenario.
        
        Args:
            trial_data: Trial information, may include 'participant_profile' 
                       with 'framing_condition' key
        
        Returns:
            Trial prompt with appropriate frame text
        """
        # Extract framing condition from participant profile
        participant_profile = trial_data.get('participant_profile', {})
        framing_condition = participant_profile.get('framing_condition')
        
        if framing_condition:
            # Load frame-specific material (positive_frame.txt or negative_frame.txt)
            frame_file = self.materials_path / f"{framing_condition}.txt"
            if frame_file.exists():
                with open(frame_file, 'r') as f:
                    frame_text = f.read().strip()
                # Add frame text to trial data for template
                trial_data = {**trial_data, 'scenario': frame_text, 'frame': framing_condition}
        
        # Use parent class method to handle template filling
        if self.trial_template:
            return self._fill_template(self.trial_template, trial_data)
        else:
            return self._build_generic_trial_prompt(trial_data)



@StudyConfigRegistry.register("study_003")
class Study003Config(BaseStudyConfig):
    """
    Tversky & Kahneman (1981) Framing Effect - Asian Disease Problem
    
    Classic demonstration of framing effect: identical options produce
    different choices depending on gain vs loss framing.
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Framing study parameters
        self.frames = ["positive_frame", "negative_frame"]
        self.options = ["Program A", "Program B"]
    
    
    def get_prompt_builder(self) -> PromptBuilder:
        """
        Return Study 003 specific PromptBuilder.
        
        Returns:
            Study003PromptBuilder instance that handles framing conditions
        """
        return Study003PromptBuilder(self.study_path)
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles based on original study's recruitment.
        
        Original study (Tversky & Kahneman, 1981):
        - N = 152 university students and faculty
        - No specific age, gender, or demographic data reported
        - Between-subjects design: 76 per condition (positive/negative frame)
        
        This method generates profiles faithful to the original:
        - Age: University population (students 18-25, faculty 30-65)
        - Gender: Not specified, so not included in profile
        - Education: Mix of students and faculty
        - Frame assignment: Random 50/50 split
        
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
        
        # Determine number per frame (should be equal for between-subjects)
        n_positive = n_participants // 2
        n_negative = n_participants - n_positive
        
        # Create frames list for assignment
        frames = ["positive_frame"] * n_positive + ["negative_frame"] * n_negative
        random.shuffle(frames)
        
        # Original study: "university students and faculty"
        # We model this as ~70% students, ~30% faculty (reasonable university mix)
        for i in range(n_participants):
            is_faculty = np.random.random() < 0.3
            
            if is_faculty:
                # Faculty: age 30-65, typically 40-50
                age = int(np.clip(np.random.normal(45, 8), 30, 65))
                education = "university_faculty"
                background = "You are a university faculty member who regularly makes decisions involving statistical reasoning and risk assessment."
            else:
                # Students: age 18-25, typically 20-22
                age = int(np.clip(np.random.normal(21, 2), 18, 25))
                education = "university_student"
                background = "You are a university student who considers different perspectives when making decisions."
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": education,
                "background": background,
                "framing_condition": frames[i],  # Critical: assign frame here
                # Note: gender not included as it was not reported in original study
                # Note: personality traits not included as this is a cognitive bias study
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial for Asian Disease Problem.
        
        Each participant gets one trial in their assigned frame condition.
        
        Args:
            n_trials: Ignored for this study (always 1 trial per participant)
        
        Returns:
            Single trial dictionary
        """
        # This is a between-subjects design with single trial
        # Frame assignment happens at participant level
        return [{
            "trial_number": 1,
            "study_type": "framing_effect",
            "trial_type": "main_choice",
            "scenario": "asian_disease_problem",
            "expected_deaths": 600,
            "program_A_certain": 200,  # 200 saved / 400 die
            "program_B_probability_all": 1/3,
            "program_B_probability_none": 2/3,
            "correct_answer": None,  # No objectively correct answer
            "frame": "assigned_by_condition"  # Set by participant profile
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate framing effect results.
        
        Computes:
        1. Choice proportions by frame
        2. Framing effect size (difference in certain choice proportion)
        3. Statistical significance test
        4. Risk attitude by frame
        
        Args:
            raw_results: Raw results from ParticipantPool.run_experiment()
        
        Returns:
            Enhanced results with framing effect analysis
        """
        individual_data = raw_results.get("individual_data", [])
        
        if not individual_data:
            return raw_results
        
        # Separate by frame condition
        positive_frame_data = []
        negative_frame_data = []
        
        for participant in individual_data:
            frame = participant.get("profile", {}).get("framing_condition", "positive_frame")
            if frame == "positive_frame":
                positive_frame_data.append(participant)
            else:
                negative_frame_data.append(participant)
        
        # Count choices by frame
        pos_frame_choices = self._count_choices(positive_frame_data)
        neg_frame_choices = self._count_choices(negative_frame_data)
        
        # Calculate proportions
        n_positive = len(positive_frame_data)
        n_negative = len(negative_frame_data)
        
        if n_positive == 0 or n_negative == 0:
            return raw_results
        
        pos_certain_prop = pos_frame_choices["Program A"] / n_positive if n_positive > 0 else 0
        pos_risky_prop = pos_frame_choices["Program B"] / n_positive if n_positive > 0 else 0
        neg_certain_prop = neg_frame_choices["Program A"] / n_negative if n_negative > 0 else 0
        neg_risky_prop = neg_frame_choices["Program B"] / n_negative if n_negative > 0 else 0
        
        # Framing effect: difference in certain option choice
        framing_effect_size = pos_certain_prop - neg_certain_prop
        
        # Statistical test: chi-square test of independence
        # Contingency table: [positive_A, positive_B; negative_A, negative_B]
        contingency_table = np.array([
            [pos_frame_choices["Program A"], pos_frame_choices["Program B"]],
            [neg_frame_choices["Program A"], neg_frame_choices["Program B"]]
        ])
        
        # Try chi-square test, but handle case where expected frequencies are too low
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        except ValueError as e:
            # If chi-square fails (e.g., zero cells), report NaN
            print(f"⚠️  Warning: Chi-square test failed - {e}")
            print(f"   Contingency table: {contingency_table.tolist()}")
            print(f"   This usually means insufficient variation in responses.")
            chi2, p_value, dof = float('nan'), float('nan'), 1
        
        # Build enhanced results matching ground_truth structure
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": {
                "by_frame": {
                    "positive_frame": {
                        "n": n_positive,
                        "option_A_count": pos_frame_choices["Program A"],
                        "option_B_count": pos_frame_choices["Program B"],
                        "option_A_proportion": pos_certain_prop,
                        "option_B_proportion": pos_risky_prop,
                        "risk_averse_proportion": pos_certain_prop,
                        "risk_seeking_proportion": pos_risky_prop
                    },
                    "negative_frame": {
                        "n": n_negative,
                        "option_A_count": neg_frame_choices["Program A"],
                        "option_B_count": neg_frame_choices["Program B"],
                        "option_A_proportion": neg_certain_prop,
                        "option_B_proportion": neg_risky_prop,
                        "risk_averse_proportion": neg_risky_prop,  # In negative frame, Program B avoids certain loss
                        "risk_seeking_proportion": neg_certain_prop
                    }
                },
                "overall": {
                    "n": n_positive + n_negative,
                    "mean_certain_choice_positive": pos_certain_prop,
                    "mean_certain_choice_negative": neg_certain_prop,
                    "framing_effect_size": framing_effect_size,
                    "framing_effect_note": f"{abs(framing_effect_size)*100:.1f} percentage point difference"
                },
                # Add top-level fields for scorer to find
                "positive_frame_option_A_proportion": pos_certain_prop,
                "negative_frame_option_B_proportion": neg_risky_prop,
                "framing_effect_size": framing_effect_size
            },
            "inferential_statistics": {
                "main_effect": {
                    "test_type": "chi_square",
                    "statistic": f"χ²({dof}) = {chi2:.2f}",
                    "chi_square": float(chi2),
                    "degrees_of_freedom": int(dof),
                    "p_value": float(p_value),
                    "p": float(p_value),  # Add alias for compatibility
                    "p_value_note": f"p = {p_value:.4f}" if p_value >= 0.001 else "p < 0.001",
                    "significant": bool(p_value < 0.05),
                    "effect_interpretation": self._interpret_effect(framing_effect_size, p_value)
                }
            },
            "framing_analysis": {
                "positive_frame_risk_aversion": bool(pos_certain_prop > 0.5),
                "negative_frame_risk_seeking": bool(neg_risky_prop > 0.5),
                "preference_reversal": bool((pos_certain_prop > 0.5) and (neg_risky_prop > 0.5)),
                "effect_direction_correct": bool(framing_effect_size > 0.30)
            }
        }
        
        return enhanced_results
    
    def _count_choices(self, participant_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count Program A vs Program B choices."""
        counts = {"Program A": 0, "Program B": 0}
        
        for participant in participant_data:
            # Get choice from responses (key is "responses", not "trial_results")
            responses = participant.get("responses", [])
            if responses:
                last_response = responses[-1]
                response_text = last_response.get("response_text", "").strip()
                response = last_response.get("response", "").strip()
                
                # Check both response and response_text
                combined = (response + " " + response_text).upper()
                
                # Normalize response - look for A or B in the text
                if "PROGRAM A" in combined or response.upper() == "A":
                    counts["Program A"] += 1
                elif "PROGRAM B" in combined or response.upper() == "B":
                    counts["Program B"] += 1
        
        return counts
    
    def _interpret_effect(self, effect_size: float, p_value: float) -> str:
        """Interpret the framing effect."""
        if p_value >= 0.05:
            return "No significant framing effect detected"
        
        if effect_size >= 0.50:
            return "Very strong framing effect (preference reversal >50pp)"
        elif effect_size >= 0.40:
            return "Strong framing effect consistent with original study"
        elif effect_size >= 0.30:
            return "Moderate framing effect"
        elif effect_size >= 0.20:
            return "Small but significant framing effect"
        else:
            return "Minimal framing effect"
    
    def get_custom_prompt_context(self, trial: Dict[str, Any], 
                                  participant_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide frame-specific prompt context.
        
        Args:
            trial: Trial data
            participant_profile: Participant profile with framing_condition
        
        Returns:
            Context dict with appropriate frame
        """
        frame = participant_profile.get("framing_condition", "positive_frame")
        
        # Load appropriate frame materials
        materials_path = self.study_path / "materials"
        
        if frame == "positive_frame":
            scenario_file = materials_path / "positive_frame.txt"
        else:
            scenario_file = materials_path / "negative_frame.txt"
        
        with open(scenario_file, "r") as f:
            scenario_text = f.read().strip()
        
        return {
            "frame": frame,
            "scenario": scenario_text,
            "response_format": "Please respond with either 'Program A' or 'Program B'."
        }
