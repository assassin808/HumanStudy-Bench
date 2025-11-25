"""
Study 002 Configuration - Jacowitz & Kahneman (1995)
Measures of Anchoring in Estimation Tasks
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
from scipy import stats
import re

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study002PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 002 (Anchoring).
    
    Handles loading specific question materials based on the assigned
    question and anchor condition.
    """
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with question-specific content.
        
        Args:
            trial_data: Trial information including specific 'question' and 'anchor_condition'
        
        Returns:
            Trial prompt with appropriate anchor and question
        """
        # Get question and anchor from trial data (now explicitly specified in create_trials)
        question_id = trial_data.get('question', 'mississippi')
        anchor_condition = trial_data.get('anchor_condition', 'high')
        
        # Construct filename: e.g., "mississippi_high.txt"
        filename = f"{question_id}_{anchor_condition}.txt"
        material_file = self.materials_path / filename
        
        content = ""
        if material_file.exists():
            with open(material_file, 'r') as f:
                content = f.read()
        else:
            content = f"Error: Material file {filename} not found."
            
        # Append standard formatting instruction
        formatting_instruction = (
            "\n\nPlease provide your answer in the following format:\n"
            "Comparison: [Higher/Lower]\n"
            "Estimate: [Your numerical estimate]\n"
            "Confidence: [1-10]"
        )
        
        return content + formatting_instruction


@StudyConfigRegistry.register("study_002")
class Study002Config(BaseStudyConfig):
    """
    Jacowitz & Kahneman (1995) Anchoring Effect
    
    Classic demonstration that arbitrary anchor values systematically
    bias numerical estimates, even when anchors are known to be random.
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Study parameters - 15 estimation questions from Jacowitz & Kahneman (1995)
        self.questions = [
            "mississippi", "everest", "meat", "sf_nyc", "redwood", 
            "un_members", "female_profs", "chicago", "telephone", "babies",
            "cat_speed", "gas_usage", "bars_berkeley", "colleges_ca", "lincoln"
        ]
        self.anchor_conditions = ["high", "low"]
        
        # Question Data (from Table 1 of the paper)
        # calibration_median is used as the "reference" or "correct" answer proxy
        self.question_info = {
            "mississippi": {"text": "Length of Mississippi River (in miles)", "high": 2000, "low": 70, "ref": 800},
            "everest": {"text": "Height of Mount Everest (in feet)", "high": 45500, "low": 2000, "ref": 12000},
            "meat": {"text": "Amount of meat eaten per year by average American (in pounds)", "high": 1000, "low": 50, "ref": 180},
            "sf_nyc": {"text": "Distance from San Francisco to New York City (in miles)", "high": 6000, "low": 1500, "ref": 3200},
            "redwood": {"text": "Height of tallest redwood (in feet)", "high": 550, "low": 65, "ref": 200},
            "un_members": {"text": "Number of United Nations members", "high": 127, "low": 14, "ref": 50},
            "female_profs": {"text": "Number of female professors at the University of California, Berkeley", "high": 130, "low": 25, "ref": 50},
            "chicago": {"text": "Population of Chicago (in millions)", "high": 5.0, "low": 0.2, "ref": 1.0},
            "telephone": {"text": "Year telephone was invented", "high": 1920, "low": 1850, "ref": 1889},
            "babies": {"text": "Average number of babies born per day in the United States", "high": 50000, "low": 100, "ref": 2000},
            "cat_speed": {"text": "Maximum speed of house cat (in miles per hour)", "high": 30, "low": 7, "ref": 18},
            "gas_usage": {"text": "Amount of gas used per month by average American (in gallons)", "high": 80, "low": 20, "ref": 50},
            "bars_berkeley": {"text": "Number of bars in Berkeley, CA", "high": 85, "low": 10, "ref": 20},
            "colleges_ca": {"text": "Number of state colleges and universities in California", "high": 100, "low": 20, "ref": 30},
            "lincoln": {"text": "Number of Lincoln's presidency", "high": 17, "low": 7, "ref": 16}
        }
    
    def get_prompt_builder(self) -> PromptBuilder:
        return Study002PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles.
        True Within-Subjects design: Each participant answers ALL 15 questions with BOTH anchors.
        Total: 15 questions × 2 anchors = 30 trials per participant.
        """
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        profiles = []
        
        for i in range(n_participants):
            # Original study: Stanford undergrads
            age = int(np.clip(np.random.normal(20, 1.5), 18, 22))
            
            profile = {
                "participant_id": i,
                "age": age,
                "education": "college_student",
                "background": "You are a university student participating in a judgment study.",
                "design": "within_subjects"
                # No condition_map needed - each participant does all questions with both anchors
            }
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate trials for anchoring task.
        True Within-Subjects: Each question appears twice (once with high anchor, once with low).
        Returns 30 trials (15 questions × 2 anchors), randomized order.
        """
        trials = []
        
        # Generate all question-anchor combinations
        for question_id in self.questions:
            for anchor_condition in self.anchor_conditions:
                trials.append({
                    "study_type": "anchoring_effect",
                    "trial_type": "estimation",
                    "scenario": "numerical_estimation_with_anchor",
                    "question": question_id,
                    "anchor_condition": anchor_condition  # Explicitly specify anchor
                })
        
        # Randomize trial order to avoid order effects
        random.shuffle(trials)
        
        # Assign trial numbers after shuffling
        for i, trial in enumerate(trials):
            trial["trial_number"] = i + 1
            
        return trials
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate anchoring effect results.
        Now handles multiple trials per participant.
        Includes Confidence analysis.
        """
        individual_data = raw_results.get("individual_data", [])
        if not individual_data:
            # Try to handle 'participants' key if 'individual_data' is missing
            individual_data = raw_results.get("participants", [])
            
        if not individual_data:
            return {"error": "No participant data found", "n": 0}
        
        # Initialize storage
        # Structure: question -> anchor_condition -> {'estimates': [], 'confidences': []}
        data = {q: {"high": {"estimates": [], "confidences": []}, 
                    "low": {"estimates": [], "confidences": []}} 
                for q in self.questions}
        
        for p in individual_data:
            # Get all trials for this participant
            trials = p.get("trial_responses", []) or p.get("responses", [])
            
            for trial_resp in trials:
                # Extract question and anchor from trial_info (now explicitly stored)
                trial_info = trial_resp.get("trial_info", {})
                question = trial_info.get("question") or trial_resp.get("question")
                anchor = trial_info.get("anchor_condition") or trial_resp.get("anchor_condition")
                
                if not question or not anchor:
                    continue
                
                # Extract numerical response and confidence
                response_text = trial_resp.get("response_text", trial_resp.get("response", ""))
                
                val = self._parse_numeric_estimate(str(response_text))
                conf = self._parse_confidence(str(response_text))
                
                if val is not None and question in data and anchor in ["high", "low"]:
                    data[question][anchor]["estimates"].append(val)
                    if conf is not None:
                        data[question][anchor]["confidences"].append(conf)
        
        # Compute stats
        results = {
            "n_total": len(individual_data),
            "by_question": {},
            "overall_anchoring_index": 0.0,
            "mean_anchoring_index": 0.0, # Alias for compatibility
            "overall_confidence": 0.0,
            "mean_confidence": 0.0, # Alias for compatibility
            "anchoring_indices": [],
            "all_confidences": []
        }
        
        total_ai = 0
        valid_questions = 0
        all_confidences = []
        all_ais = []
        
        for q in self.questions:
            high_vals = data[q]["high"]["estimates"]
            low_vals = data[q]["low"]["estimates"]
            
            high_confs = data[q]["high"]["confidences"]
            low_confs = data[q]["low"]["confidences"]
            
            mean_high = np.mean(high_vals) if high_vals else 0
            mean_low = np.mean(low_vals) if low_vals else 0
            
            median_high = np.median(high_vals) if high_vals else 0
            median_low = np.median(low_vals) if low_vals else 0
            
            mean_conf_high = np.mean(high_confs) if high_confs else 0
            mean_conf_low = np.mean(low_confs) if low_confs else 0
            
            if high_confs: all_confidences.extend(high_confs)
            if low_confs: all_confidences.extend(low_confs)
            
            # Calculate Anchoring Index (AI) using MEDIANS as per Jacowitz & Kahneman (1995)
            # AI = (Median_High - Median_Low) / (Anchor_High - Anchor_Low)
            anchor_high = self.question_info[q]["high"]
            anchor_low = self.question_info[q]["low"]
            denominator = anchor_high - anchor_low
            
            ai = (median_high - median_low) / denominator if denominator != 0 else 0
            
            # T-test
            t_stat, p_val = 0.0, 1.0
            if len(high_vals) > 1 and len(low_vals) > 1:
                # Check for zero variance
                if np.std(high_vals) == 0 and np.std(low_vals) == 0:
                    p_val = 1.0 if mean_high == mean_low else 0.0
                else:
                    try:
                        t_stat, p_val = stats.ttest_ind(high_vals, low_vals, equal_var=False)
                    except Exception:
                        pass
            
            results["by_question"][q] = {
                "high_n": len(high_vals),
                "low_n": len(low_vals),
                "high_mean": float(mean_high),
                "low_mean": float(mean_low),
                "high_confidence": float(mean_conf_high),
                "low_confidence": float(mean_conf_low),
                "anchoring_index": float(ai),
                "p_value": float(p_val) if not np.isnan(p_val) else 1.0
            }
            
            # After calculating AI
            if len(high_vals) > 0 and len(low_vals) > 0:
                total_ai += ai
                valid_questions += 1
                all_ais.append(ai)
                
        results["overall_anchoring_index"] = float(total_ai / valid_questions) if valid_questions > 0 else 0.0
        results["mean_anchoring_index"] = results["overall_anchoring_index"]
        results["overall_confidence"] = float(np.mean(all_confidences)) if all_confidences else 0.0
        results["mean_confidence"] = results["overall_confidence"]
        results["anchoring_indices"] = all_ais
        results["all_confidences"] = all_confidences
        
        return results

    def _parse_confidence(self, text: str) -> Optional[float]:
        """Extract confidence score (1-10)."""
        import re
        # Look for "Confidence: X"
        match = re.search(r"Confidence:\s*(\d+)", text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                # Clip to valid range 1-10
                return max(1.0, min(10.0, val))
            except ValueError:
                pass
        return None

    def _parse_numeric_estimate(self, text: str) -> Optional[float]:
        """
        Extract numeric estimate from text, prioritizing 'Estimate:' format.
        Robust against commas and other artifacts.
        """
        # 1. Try to find explicit "Estimate:" pattern first
        estimate_match = re.search(r"Estimate:\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if estimate_match:
            num_str = estimate_match.group(1).replace(",", "")
            try:
                return float(num_str)
            except ValueError:
                pass
        
        # 2. Fallback: Look for the last number in the text
        # This is safer than first number because the anchor (first number) is usually at the start
        # But "last number" might be confidence (1-10).
        # So let's try to filter out single digit integers at the very end if confidence is requested.
        # Given the new format, Confidence is at the end. Estimate is in the middle.
        
        # Let's try to be smarter.
        # Remove the anchor value from consideration if possible? No, that's hard.
        # If the text contains "Confidence:", strip everything after it.
        
        clean_text = text
        if "Confidence:" in text:
            clean_text = text.split("Confidence:")[0]
            
        # Now extract numbers from what remains
        # Remove commas
        clean_text = clean_text.replace(",", "")
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", clean_text)
        
        if matches:
            # If explicit "Estimate:" wasn't found, we might still be here.
            # If we have multiple numbers, the anchor is likely the first one if they repeated the question.
            # The estimate is likely the second one or the last one before confidence.
            
            # Heuristic: if there are multiple numbers, pick the one that is NOT the anchor (if we knew it)
            # or just pick the last one found in the "Estimate" section.
            try:
                return float(matches[-1])
            except ValueError:
                return None
                
        return None
