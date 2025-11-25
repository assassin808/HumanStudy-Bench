"""
Study 006 Configuration - Goldstein, Cialdini, & Griskevicius (2008)
Social Norms and Environmental Conservation in Hotels

Implementation of field experiment examining how descriptive social norms
motivate hotel guests to participate in towel reuse programs.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study006PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 006 (Social Norms and Conservation).
    
    Handles message-specific prompt generation by loading appropriate
    material files based on participant's assigned message condition.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with message-specific content.
        
        Args:
            trial_data: Trial information including 'participant_profile'
                       with 'message_condition' key
        
        Returns:
            Trial prompt with appropriate message content
        """
        participant_profile = trial_data.get('participant_profile', {})
        message_condition = participant_profile.get('message_condition', 'environmental')
        
        # Map message conditions to file names
        message_files = {
            'environmental': 'environmental_message.txt',
            'descriptive_norm_guest': 'descriptive_norm_guest.txt',
            'descriptive_norm_room': 'descriptive_norm_room.txt',
            'descriptive_norm_citizen': 'descriptive_norm_citizen.txt',
            'descriptive_norm_gender': 'descriptive_norm_gender.txt'
        }
        
        # Load message-specific material
        message_file = message_files.get(message_condition, 'environmental_message.txt')
        material_file = self.materials_path / message_file
        
        if material_file.exists():
            with open(material_file, 'r') as f:
                message_text = f.read()
            
            # Fill template if needed (e.g., room number for descriptive_norm_room)
            if message_condition == 'descriptive_norm_room':
                # Use participant_id or generate room number
                room_number = participant_profile.get('room_number') or f"{participant_profile.get('participant_id', 0) % 500 + 100}"
                message_text = message_text.replace('{{room_number}}', str(room_number))
            
            return message_text
        
        # Fallback
        return self._build_generic_trial_prompt(trial_data)


@StudyConfigRegistry.register("study_006")
class Study006Config(BaseStudyConfig):
    """
    Goldstein, Cialdini, & Griskevicius (2008) Social Norms and Conservation
    
    Field experiment demonstrating that descriptive normative messages
    (informing guests that most others participate) significantly outperform
    traditional environmental protection messages in motivating hotel towel reuse.
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Study parameters
        self.message_conditions = [
            "environmental",
            "descriptive_norm_guest",
            "descriptive_norm_room",
            "descriptive_norm_citizen",
            "descriptive_norm_gender"
        ]
    
    def get_prompt_builder(self) -> PromptBuilder:
        """
        Return Study 006 specific PromptBuilder.
        
        Returns:
            Study006PromptBuilder instance that handles message-specific prompts
        """
        return Study006PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles with message condition assignment.
        
        Original study (Goldstein et al., 2008):
        - N = 1595 (Experiment 2)
        - Hotel guests staying minimum 2 nights
        - Random assignment to 5 message conditions
        - Between-subjects design
        
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
        
        # Assign message conditions (equal distribution across 5 conditions)
        n_per_condition = n_participants // 5
        remainder = n_participants % 5
        
        condition_assignments = []
        for i, condition in enumerate(self.message_conditions):
            count = n_per_condition + (1 if i < remainder else 0)
            condition_assignments.extend([condition] * count)
        
        random.shuffle(condition_assignments)
        
        for i in range(n_participants):
            # Original study: hotel guests, ages vary
            # No specific age distribution reported, use general adult range
            age = int(np.clip(np.random.normal(40, 15), 18, 80))
            
            # Assign room number (for descriptive_norm_room condition)
            room_number = f"{100 + (i % 400)}"
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": "adult_general_population",
                "background": "You are a hotel guest staying at a hotel that has an environmental conservation program.",
                "message_condition": condition_assignments[i],
                "room_number": room_number,
                "design": "between_subjects"
            }
            
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial for towel reuse decision.
        
        Each participant makes one decision about whether to participate
        in the towel reuse program.
        
        Args:
            n_trials: Ignored for this study (always 1 trial per participant)
        
        Returns:
            Single trial dictionary
        """
        # This is a between-subjects design with single decision
        # Message condition assignment happens at participant level
        return [{
            "trial_number": 1,
            "study_type": "social_norms_conservation",
            "trial_type": "critical",
            "scenario": "hotel_towel_reuse_program",
            "decision_type": "towel_reuse_participation"
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate results from raw participant responses.
        
        Args:
            raw_results: Raw results dictionary with participant responses
        
        Returns:
            Aggregated results with descriptive statistics by message condition
        """
        participants = raw_results.get("participants", [])
        
        if not participants:
            return {
                "error": "No participant data found",
                "n": 0
            }
        
        # Separate by message condition
        condition_responses = {condition: [] for condition in self.message_conditions}
        
        for participant in participants:
            condition = participant.get("message_condition", "unknown")
            responses = participant.get("trial_responses", [])
            
            # Check if participant reused towels (participated)
            # Response format: "A) Participate" or "B) Not Participate"
            # Also supports: "A", "Participate", "B", "Not Participate", etc.
            participated = False
            if responses:
                response = responses[0].get("response", "").strip()
                response_upper = response.upper()
                
                # Check for explicit "A) Participate" or "A" format
                if response_upper.startswith("A") or "A)" in response_upper:
                    participated = True
                # Check for explicit "B) Not Participate" or "B" format
                elif response_upper.startswith("B") or "B)" in response_upper:
                    participated = False
                # Fallback: keyword matching (backward compatibility)
                else:
                    response_lower = response.lower()
                    participated = any(keyword in response_lower for keyword in [
                        "participate", "yes", "reuse", "will reuse", "agree", "ok"
                    ]) and not any(keyword in response_lower for keyword in [
                        "not participate", "no", "don't", "won't", "refuse"
                    ])
            
            if condition in condition_responses:
                condition_responses[condition].append({
                    "participant_id": participant.get("participant_id"),
                    "participated": participated,
                    "towel_reuse_rate": 1.0 if participated else 0.0
                })
        
        # Calculate descriptive statistics for each condition
        result = {
            "n_total": len(participants),
            "by_condition": {}
        }
        
        for condition in self.message_conditions:
            responses = condition_responses[condition]
            if responses:
                participation_rates = [r["towel_reuse_rate"] for r in responses]
                
                result["by_condition"][condition] = {
                    "n": len(responses),
                    "towel_reuse_rate": np.mean(participation_rates),
                    "sd": np.std(participation_rates, ddof=1) if len(responses) > 1 else 0.0,
                    "towel_reuse_count": sum(participation_rates),
                    "non_participation_count": len(responses) - sum(participation_rates)
                }
            else:
                result["by_condition"][condition] = {
                    "n": 0,
                    "towel_reuse_rate": 0.0,
                    "sd": 0.0,
                    "towel_reuse_count": 0,
                    "non_participation_count": 0
                }
        
        # Calculate combined descriptive norms rate
        descriptive_norm_conditions = [
            "descriptive_norm_guest",
            "descriptive_norm_room",
            "descriptive_norm_citizen",
            "descriptive_norm_gender"
        ]
        
        all_descriptive_responses = []
        for condition in descriptive_norm_conditions:
            all_descriptive_responses.extend(condition_responses[condition])
        
        if all_descriptive_responses:
            descriptive_rates = [r["towel_reuse_rate"] for r in all_descriptive_responses]
            result["descriptive_norms_combined"] = {
                "n": len(all_descriptive_responses),
                "towel_reuse_rate": np.mean(descriptive_rates),
                "sd": np.std(descriptive_rates, ddof=1) if len(descriptive_rates) > 1 else 0.0,
                "towel_reuse_count": sum(descriptive_rates)
            }
        
        return result

