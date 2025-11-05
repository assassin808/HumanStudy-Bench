"""
Study 002 Configuration - Jacowitz & Kahneman Anchoring Effect (1995)

Implementation of classic anchoring in estimation tasks.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study002PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 002 (Anchoring Effect).
    
    Handles question-specific prompt generation by loading appropriate
    material files based on participant's assigned question and anchor condition.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with question-specific scenario and anchor.
        
        Args:
            trial_data: Trial information including 'participant_profile' 
                       with 'question' and 'anchor_condition' keys
        
        Returns:
            Trial prompt with appropriate question and anchor
        """
        # Extract assignments from participant profile
        participant_profile = trial_data.get('participant_profile', {})
        question = participant_profile.get('question', 'washington')
        anchor_condition = participant_profile.get('anchor_condition', 'high')
        
        # Add minimal fields for trial tracking
        trial_data["question"] = question
        trial_data["anchor_condition"] = anchor_condition
        trial_data["trial_type"] = "estimation"
        
        # Load question-specific material for prompt
        # Format: {question}_{anchor_condition}.txt
        material_file = self.materials_path / f"{question}_{anchor_condition}.txt"
        if material_file.exists():
            with open(material_file, 'r') as f:
                problem_text = f.read().strip()
            return problem_text
        
        # Fallback
        return self._build_generic_trial_prompt(trial_data)


@StudyConfigRegistry.register("study_002")
class Study002Config(BaseStudyConfig):
    """
    Jacowitz & Kahneman (1995) Anchoring Effect
    
    Classic demonstration that arbitrary anchor values systematically
    bias numerical estimates, even when anchors are known to be random.
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Study parameters - 3 estimation questions
        self.questions = ["washington", "chicago", "everest"]
        self.anchor_conditions = ["high", "low"]
        
        # Anchor values and correct answers
        self.question_info = {
            "washington": {
                "high_anchor": 1920,
                "low_anchor": 1700,
                "correct_answer": 1789
            },
            "chicago": {
                "high_anchor": 5.0,
                "low_anchor": 0.2,
                "correct_answer": 2.7
            },
            "everest": {
                "high_anchor": 180,
                "low_anchor": 100,
                "correct_answer": 160
            }
        }
    
    def get_prompt_builder(self) -> PromptBuilder:
        """
        Return Study 002 specific PromptBuilder.
        
        Returns:
            Study002PromptBuilder instance that handles question-specific prompts
        """
        return Study002PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles based on original study's recruitment.
        
        Original study (Jacowitz & Kahneman, 1995):
        - N = 145 Stanford undergraduates
        - Ages 18-22 (typical undergraduate range)
        - Between-subjects design: each participant gets ONE question 
          with EITHER high or low anchor
        - 2x3 factorial: 2 anchor conditions × 3 questions
        
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
        
        # Create balanced assignment: 2 conditions × 3 questions = 6 cells
        # Each cell gets n_participants / 6 participants
        cells = []
        for question in self.questions:
            for anchor in self.anchor_conditions:
                cells.append((question, anchor))
        
        # Assign participants evenly to cells
        n_per_cell = n_participants // len(cells)
        remainder = n_participants % len(cells)
        
        assignments = []
        for i, cell in enumerate(cells):
            n_this_cell = n_per_cell + (1 if i < remainder else 0)
            assignments.extend([cell] * n_this_cell)
        
        random.shuffle(assignments)
        
        for i in range(n_participants):
            # Original study: Stanford undergrads ages 18-22
            age = int(np.clip(np.random.normal(20, 1.2), 18, 22))
            
            question, anchor = assignments[i]
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": "college_student",
                "background": "You are a college student answering estimation questions.",
                "question": question,  # Between-subjects: ONE question per participant
                "anchor_condition": anchor,  # Between-subjects: high OR low anchor
                "design": "between_subjects"
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial for anchoring task.
        
        Each participant gets ONE trial with their assigned question and anchor.
        Between-subjects design: both question and anchor assigned at participant level.
        
        Args:
            n_trials: Ignored for this study (always 1 trial per participant)
        
        Returns:
            Single trial dictionary
        """
        # This is a between-subjects design with single trial
        # Question and anchor assignment happens at participant level
        return [{
            "trial_number": 1,
            "study_type": "anchoring_effect",
            "trial_type": "estimation",
            "scenario": "numerical_estimation_with_anchor"
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate anchoring effect results.
        
        Computes:
        1. Mean estimates for high vs low anchor conditions per question
        2. Anchoring index: (Mean_high - Mean_low) / (Anchor_high - Anchor_low)
        3. Statistical significance tests (t-tests)
        4. Effect sizes (Cohen's d)
        
        Args:
            raw_results: Raw results from ParticipantPool.run_experiment()
        
        Returns:
            Enhanced results with anchoring effect analysis
        """
        individual_data = raw_results.get("individual_data", [])
        
        if not individual_data:
            return raw_results
        
        # Organize estimates by question and anchor condition
        estimates = {
            "washington": {"high": [], "low": []},
            "chicago": {"high": [], "low": []},
            "everest": {"high": [], "low": []}
        }
        
        # Extract estimates from individual data
        for participant in individual_data:
            profile = participant.get("profile", {})
            question = profile.get("question")
            anchor_condition = profile.get("anchor_condition")
            
            if not question or not anchor_condition:
                continue
            
            responses = participant.get("responses", [])
            for response in responses:
                response_text = response.get("response") or response.get("response_text", "")
                if not response_text or response_text == "None":
                    continue
                
                # Parse numeric estimate
                estimate = self._parse_numeric_estimate(str(response_text))
                if estimate is not None:
                    estimates[question][anchor_condition].append(estimate)
        
        # Compute statistics for each question
        question_results = {}
        anchoring_indices = []
        cohens_ds = []
        
        for question in self.questions:
            high_estimates = estimates[question]["high"]
            low_estimates = estimates[question]["low"]
            
            if len(high_estimates) < 2 or len(low_estimates) < 2:
                # Not enough data
                question_results[question] = {
                    "n_high": len(high_estimates),
                    "n_low": len(low_estimates),
                    "insufficient_data": True
                }
                continue
            
            # Compute means and SDs
            mean_high = np.mean(high_estimates)
            mean_low = np.mean(low_estimates)
            sd_high = np.std(high_estimates, ddof=1)
            sd_low = np.std(low_estimates, ddof=1)
            
            # Independent samples t-test
            t_stat, p_value = stats.ttest_ind(high_estimates, low_estimates)
            
            # Effect size (Cohen's d)
            pooled_sd = np.sqrt(((len(high_estimates) - 1) * sd_high**2 + 
                                 (len(low_estimates) - 1) * sd_low**2) / 
                                (len(high_estimates) + len(low_estimates) - 2))
            cohens_d = (mean_high - mean_low) / pooled_sd if pooled_sd > 0 else 0
            
            # Anchoring index
            anchor_high = self.question_info[question]["high_anchor"]
            anchor_low = self.question_info[question]["low_anchor"]
            anchoring_index = (mean_high - mean_low) / (anchor_high - anchor_low)
            
            question_results[question] = {
                "n_high": len(high_estimates),
                "n_low": len(low_estimates),
                "mean_high": float(mean_high),
                "mean_low": float(mean_low),
                "sd_high": float(sd_high),
                "sd_low": float(sd_low),
                "anchor_high": anchor_high,
                "anchor_low": anchor_low,
                "correct_answer": self.question_info[question]["correct_answer"],
                "anchoring_index": float(anchoring_index),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "cohens_d": float(cohens_d),
                "significant": bool(p_value < 0.05),
                "interpretation": self._interpret_anchoring(anchoring_index, p_value)
            }
            
            anchoring_indices.append(anchoring_index)
            cohens_ds.append(cohens_d)
        
        # Overall statistics
        if anchoring_indices:
            mean_anchoring_index = np.mean(anchoring_indices)
            mean_cohens_d = np.mean(cohens_ds)
            all_significant = all(
                question_results[q].get("significant", False) 
                for q in self.questions 
                if not question_results[q].get("insufficient_data", False)
            )
        else:
            mean_anchoring_index = 0
            mean_cohens_d = 0
            all_significant = False
        
        # Build enhanced results
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": {
                "washington": question_results.get("washington", {}),
                "chicago": question_results.get("chicago", {}),
                "everest": question_results.get("everest", {}),
                "overall": {
                    "mean_anchoring_index": float(mean_anchoring_index),
                    "mean_cohens_d": float(mean_cohens_d),
                    "all_effects_significant": all_significant,
                    "interpretation": self._interpret_overall_anchoring(mean_anchoring_index)
                }
            },
            "inferential_statistics": {
                "washington_effect": self._build_effect_dict(question_results.get("washington", {})),
                "chicago_effect": self._build_effect_dict(question_results.get("chicago", {})),
                "everest_effect": self._build_effect_dict(question_results.get("everest", {}))
            },
            "anchoring_analysis": {
                "exhibits_anchoring": all_significant,
                "anchoring_strength": self._categorize_anchoring_strength(mean_anchoring_index),
                "consistency": "high" if len(anchoring_indices) == 3 and np.std(anchoring_indices) < 0.15 else "moderate"
            }
        }
        
        return enhanced_results
    
    def _parse_numeric_estimate(self, response_text: str) -> Optional[float]:
        """
        Parse numeric estimate from response text.
        
        Args:
            response_text: Raw response text
        
        Returns:
            Numeric estimate or None if parsing fails
        """
        import re
        
        # Remove common text patterns
        text = response_text.upper()
        text = re.sub(r'(MY ESTIMATE IS|I ESTIMATE|ESTIMATE:|ANSWER:)', '', text)
        
        # Extract first number (integer or float)
        numbers = re.findall(r'\b(\d+\.?\d*)\b', text)
        
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
        
        return None
    
    def _interpret_anchoring(self, index: float, p_value: float) -> str:
        """Interpret anchoring effect strength."""
        if p_value >= 0.05:
            return "No significant anchoring effect"
        
        if index >= 0.5:
            return "Very strong anchoring (index ≥ 0.5)"
        elif index >= 0.4:
            return "Strong anchoring consistent with original study (index 0.4-0.5)"
        elif index >= 0.3:
            return "Moderate anchoring (index 0.3-0.4)"
        elif index >= 0.2:
            return "Weak anchoring (index 0.2-0.3)"
        else:
            return "Minimal anchoring (index < 0.2)"
    
    def _interpret_overall_anchoring(self, mean_index: float) -> str:
        """Interpret overall anchoring strength."""
        if mean_index >= 0.45:
            return "Very strong anchoring effect matching original study"
        elif mean_index >= 0.35:
            return "Strong anchoring effect similar to original study"
        elif mean_index >= 0.25:
            return "Moderate anchoring effect"
        elif mean_index >= 0.15:
            return "Weak anchoring effect"
        else:
            return "Minimal or no anchoring effect"
    
    def _categorize_anchoring_strength(self, mean_index: float) -> str:
        """Categorize anchoring strength."""
        if mean_index >= 0.5:
            return "very_strong"
        elif mean_index >= 0.4:
            return "strong"
        elif mean_index >= 0.3:
            return "moderate"
        elif mean_index >= 0.2:
            return "weak"
        else:
            return "minimal"
    
    def _build_effect_dict(self, question_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized effect dictionary for a question."""
        if question_result.get("insufficient_data", False):
            return {
                "test_type": "independent_t_test",
                "insufficient_data": True
            }
        
        return {
            "test_type": "independent_t_test",
            "t_statistic": question_result.get("t_statistic", float('nan')),
            "p_value": question_result.get("p_value", float('nan')),
            "p": question_result.get("p_value", float('nan')),
            "cohens_d": question_result.get("cohens_d", float('nan')),
            "anchoring_index": question_result.get("anchoring_index", float('nan')),
            "significant": question_result.get("significant", False),
            "conclusion": question_result.get("interpretation", "Unknown")
        }
    
    def get_custom_prompt_context(self, trial: Dict[str, Any], 
                                  participant_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide question-specific prompt context.
        
        Args:
            trial: Trial data
            participant_profile: Participant profile
        
        Returns:
            Context dict with appropriate question and anchor details
        """
        question = participant_profile.get("question", "washington")
        anchor_condition = participant_profile.get("anchor_condition", "high")
        
        question_info = self.question_info.get(question, {})
        anchor_value = question_info.get(f"{anchor_condition}_anchor")
        
        return {
            "question": question,
            "anchor_condition": anchor_condition,
            "anchor_value": anchor_value,
            "response_format": "Please provide your numerical estimate."
        }
