"""
Study 001 Configuration - Ross et al. (1977) False Consensus Effect

Implementation of the False Consensus Effect scenarios (Study 1, 2, & 3).
Study numbering in this config aligns with the original paper:
- Study 1: 4 Hypothetical Stories
- Study 2: 34-Item Questionnaire (Administered as a single full questionnaire)
- Study 3: "Eat at Joe's" / "Repent" Sign (Hypothetical/Real)
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import random
import re
import json
from scipy import stats

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


class Study001PromptBuilder(PromptBuilder):
    """
    Custom PromptBuilder for Study 001 (False Consensus Effect).
    """
    
    def __init__(self, study_path: Path):
        super().__init__(study_path)
        self.questionnaire_items = self._load_questionnaire_items()
        
    def _load_questionnaire_items(self) -> List[Dict[str, Any]]:
        try:
            items_path = self.materials_path / "study_2_items.json"
            with open(items_path, 'r') as f:
                data = json.load(f)
                return data.get("items", [])
        except Exception:
            return []
            
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build trial prompt with scenario-specific text.
        """
        # Extract scenario assignment
        participant_profile = trial_data.get('participant_profile', {})
        scenario = participant_profile.get('assigned_scenario', 'study_1_supermarket')
        
        # Case 1: Questionnaire (Study 2) - FULL Questionnaire
        if scenario == "study_2_questionnaire_full":
            return self._build_full_questionnaire_prompt()
            
        # Case 2: Standard Scenarios (Study 1 & 3)
        scenario_file = self.materials_path / f"{scenario}.txt"
        if scenario_file.exists():
            with open(scenario_file, 'r') as f:
                scenario_text = f.read().strip()
            return scenario_text
        
        return self._build_generic_trial_prompt(trial_data)

    def _build_full_questionnaire_prompt(self) -> str:
        """Build prompt containing ALL 34 items."""
        prompt = """You are participating in a survey about personal characteristics and preferences.
You will be presented with 34 items. For each item, you must:
1. Choose which option best describes YOU (Self-Categorization).
2. Estimate the percentage of "college students in general" who would fall into Option A.
3. Estimate the percentage of "college students in general" who would fall into Option B.

Please answer in a structured JSON format as a list of objects.
Example format:
[
  {"id": "shy", "my_choice": "Option A", "estimate_a": 45, "estimate_b": 55},
  ...
]

Here are the items:

"""
        for idx, item in enumerate(self.questionnaire_items, 1):
            prompt += f"""
Item {idx} (ID: {item['id']}): {item['category']}
Option A: {item['option_a']}
Option B: {item['option_b']}
"""
        
        prompt += "\nPlease provide your responses for ALL 34 items in the JSON format specified above."
        return prompt


@StudyConfigRegistry.register("study_001")
class Study001Config(BaseStudyConfig):
    """
    Ross et al. (1977) False Consensus Effect
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        self.study_1_scenarios = [
            "study_1_supermarket",
            "study_1_term_paper",
            "study_1_traffic_ticket",
            "study_1_space_program"
        ]
        self.study_3_scenarios = [
            "study_3_sign_joes",
            "study_3_sign_repent"
        ]
        
        # Load questionnaire items for Study 2
        self.questionnaire_items = self._load_questionnaire_items()
        
    def _load_questionnaire_items(self) -> List[Dict[str, Any]]:
        try:
            items_path = self.study_path / "materials" / "study_2_items.json"
            if items_path.exists():
                with open(items_path, 'r') as f:
                    data = json.load(f)
                    return data.get("items", [])
            return []
        except Exception:
            return []
    
    def get_prompt_builder(self) -> PromptBuilder:
        return Study001PromptBuilder(self.study_path)
    
    def generate_participant_profiles(self, n_participants: int, 
                                     random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate participant profiles.
        Design:
        - Study 1: 4 scenarios (Between-Subjects)
        - Study 3: 2 scenarios (Between-Subjects)
        - Study 2: 1 scenario (Full Questionnaire)
        
        We treat "Study 2 Full Questionnaire" as just another "task condition" 
        alongside the story scenarios.
        """
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        profiles = []
        
        # Create list of distinct tasks
        tasks = []
        for s in self.study_1_scenarios:
            tasks.append({"scenario": s, "type": "story"})
        for s in self.study_3_scenarios:
            tasks.append({"scenario": s, "type": "sign"})
        
        # Add Study 2 as a single task type
        tasks.append({"scenario": "study_2_questionnaire_full", "type": "questionnaire_full"})
            
        # Distribute tasks evenly
        n_tasks = len(tasks)
        assignments = []
        base_count = n_participants // n_tasks
        remainder = n_participants % n_tasks
        
        for i in range(n_tasks):
            count = base_count + (1 if i < remainder else 0)
            assignments.extend([tasks[i]] * count)
            
        random.shuffle(assignments)
        
        for i in range(n_participants):
            task = assignments[i]
            profile = {
                "participant_id": i,
                "assigned_scenario": task["scenario"],
                "design": "between_subjects", # For Study 1/3
                "task_type": task["type"]
            }
            profiles.append(profile)
        
        return profiles
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate single trial per participant.
        """
        return [{
            "trial_number": 1,
            "study_type": "false_consensus_effect",
            "trial_type": "main_scenario",
            "scenario": "assigned_by_profile"
        }]
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate results to calculate False Consensus Effect.
        """
        individual_data = raw_results.get("individual_data", [])
        if not individual_data:
            return raw_results
            
        # Structure to hold data per condition/item
        results_map = {}
        
        for participant in individual_data:
            profile = participant.get("profile", {})
            scenario = profile.get("assigned_scenario")
            
            if not scenario: continue
            
            responses = participant.get("responses", [])
            if not responses: continue
            
            resp_text = responses[0].get("response", "") or responses[0].get("response_text", "")
            
            # Handle Study 2 (Full Questionnaire)
            if scenario == "study_2_questionnaire_full":
                self._process_full_questionnaire_response(resp_text, results_map)
            else:
                # Handle Study 1 & 3 (Single Scenarios)
                self._process_single_scenario_response(scenario, resp_text, results_map)

        # Calculate statistics
        descriptive_stats = {}
        inferential_stats = {}
        all_fce_magnitudes = []
        
        for key, groups in results_map.items():
            group_a_estimates = groups['A']
            group_b_estimates = groups['B']
            
            n_a = len(group_a_estimates)
            n_b = len(group_b_estimates)
            
            mean_a = np.mean(group_a_estimates) if n_a > 0 else 0
            mean_b = np.mean(group_b_estimates) if n_b > 0 else 0
            
            fce_magnitude = mean_a - mean_b
            if n_a > 0 and n_b > 0:
                all_fce_magnitudes.append(fce_magnitude)
            
            # T-test
            if n_a > 1 and n_b > 1:
                t_stat, p_val = stats.ttest_ind(group_a_estimates, group_b_estimates, equal_var=False)
            else:
                t_stat, p_val = float('nan'), float('nan')
                
            descriptive_stats[key] = {
                "n_choice_a": n_a,
                "n_choice_b": n_b,
                "mean_estimate_by_a": mean_a,
                "mean_estimate_by_b": mean_b,
                "fce_magnitude": fce_magnitude
            }
            
            inferential_stats[f"{key}_effect"] = {
                "test_type": "t_test_ind",
                "t_statistic": float(t_stat),
                "p_value": float(p_val),
                "significant": bool(p_val < 0.05) if not np.isnan(p_val) else False
            }
            
        mean_fce = np.mean(all_fce_magnitudes) if all_fce_magnitudes else 0
        
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": {
                **descriptive_stats,
                "overall_mean_fce_magnitude": mean_fce
            },
            "inferential_statistics": inferential_stats
        }
        
        return enhanced_results

    def custom_scoring(
        self, 
        results: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """
        Score the results based on False Consensus Effect.
        
        Scores:
        - phenomenon_score: Proportion of tasks showing significant FCE in correct direction.
        - data_match_score: Similarity of FCE magnitude to human baseline.
        """
        inferential_stats = results.get("inferential_statistics", {})
        descriptive_stats = results.get("descriptive_statistics", {})
        
        # 1. Phenomenon-level Scoring
        # Check Study 1 (4 stories) and Study 3 (2 signs)
        tasks_to_check = [
            "study_1_supermarket", 
            "study_1_term_paper", 
            "study_1_traffic_ticket", 
            "study_1_space_program",
            "study_3_sign_joes",
            "study_3_sign_repent"
        ]
        
        passed_tasks = 0
        valid_tasks = 0
        
        for task in tasks_to_check:
            stats_key = f"{task}_effect"
            if stats_key in inferential_stats:
                valid_tasks += 1
                # Pass if significant (p < 0.05) AND FCE > 0 (positive bias)
                # Check descriptive stats for direction
                desc = descriptive_stats.get(task, {})
                fce_mag = desc.get("fce_magnitude", 0)
                p_val = inferential_stats[stats_key].get("p_value", 1.0)
                
                if p_val < 0.05 and fce_mag > 0:
                    passed_tasks += 1
        
        # Also check Study 2 (Questionnaire) overall
        # Study 2 has many items, we can aggregate them
        study_2_items = [k for k in descriptive_stats.keys() if k.startswith("study_2_")]
        if study_2_items:
            valid_tasks += 1
            # Calculate mean FCE and sign test
            study_2_fces = [descriptive_stats[k].get("fce_magnitude", 0) for k in study_2_items]
            mean_fce_s2 = np.mean(study_2_fces)
            # Simple sign test: proportion of items with positive FCE
            positive_items = sum(1 for x in study_2_fces if x > 0)
            prop_positive = positive_items / len(study_2_fces)
            
            if mean_fce_s2 > 0 and prop_positive > 0.6: # Pass if mostly positive
                passed_tasks += 1
        
        phenomenon_score = passed_tasks / valid_tasks if valid_tasks > 0 else 0.0
        
        # 2. Data-level Scoring (Simple deviation)
        # Compare FCE magnitudes
        total_error = 0
        count = 0
        
        # Map config keys to ground truth keys
        gt_map = {
            "study_1_supermarket": ("study_1", "study_1_supermarket"),
            "study_1_term_paper": ("study_1", "study_1_term_paper"),
            "study_1_traffic_ticket": ("study_1", "study_1_traffic_ticket"),
            "study_1_space_program": ("study_1", "study_1_space_program"),
            "study_3_sign_joes": ("study_3", "study_3_sign_joes"),
            "study_3_sign_repent": ("study_3", "study_3_sign_repent")
        }
        
        gt_results = ground_truth.get("original_results", {})
        
        for task, (section, key) in gt_map.items():
            agent_fce = descriptive_stats.get(task, {}).get("fce_magnitude")
            if agent_fce is not None:
                human_fce = gt_results.get(section, {}).get(key, {}).get("fce", 0)
                # Normalized error (relative to human FCE, capped at 1.0)
                if human_fce != 0:
                    error = abs(agent_fce - human_fce) / abs(human_fce)
                    total_error += min(error, 1.0) # Cap error at 100%
                    count += 1
        
        data_match_score = 1.0 - (total_error / count) if count > 0 else 0.0
        
        return {
            "phenomenon_level_score": float(phenomenon_score),
            "data_level_score": float(data_match_score),
            "overall_score": float((phenomenon_score * 2.0 + data_match_score * 1.0) / 3.0)
        }

    def _process_single_scenario_response(self, key: str, text: str, results_map: Dict):
        if key not in results_map:
            results_map[key] = {'A': [], 'B': []}
            
        choice = self._extract_choice(text)
        estimate = self._extract_estimate(text)
        
        if choice and estimate is not None:
            results_map[key][choice].append(estimate)

    def _process_full_questionnaire_response(self, text: str, results_map: Dict):
        """Parse JSON list response from full questionnaire."""
        try:
            # Try to find JSON list in text
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                items = json.loads(json_str)
                
                for item in items:
                    item_id = item.get('id')
                    if not item_id: continue
                    
                    key = f"study_2_{item_id}"
                    if key not in results_map:
                        results_map[key] = {'A': [], 'B': []}
                    
                    choice_text = str(item.get('my_choice', '')).upper()
                    if 'A' in choice_text: choice = 'A'
                    elif 'B' in choice_text: choice = 'B'
                    else: continue
                    
                    # Estimate for Option A
                    est_a = item.get('estimate_a')
                    if est_a is not None:
                        results_map[key][choice].append(float(est_a))
                        
        except Exception as e:
            # Fallback: if JSON parsing fails, we lose this participant's data for Study 2
            pass

    def _extract_choice(self, text: str) -> Optional[str]:
        """Extract choice A or B from text (for single scenarios)."""
        text = text.upper()
        if "OPTION A" in text and "OPTION B" not in text: return 'A'
        if "OPTION B" in text and "OPTION A" not in text: return 'B'
        if re.search(r"CHOOSE.*?A", text): return 'A'
        if re.search(r"CHOOSE.*?B", text): return 'B'
        if "A" in text[:50] and "B" not in text[:50]: return 'A'
        if "B" in text[:50] and "A" not in text[:50]: return 'B'
        return None

    def _extract_estimate(self, text: str) -> Optional[float]:
        """Extract percentage estimate for Option A (for single scenarios)."""
        text = text.replace("\n", " ")
        matches_q2 = re.findall(r"2\.\s*(\d+(?:\.\d+)?)\s*%", text)
        if matches_q2:
            return float(matches_q2[0])
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
        if matches:
            return float(matches[0])
        numbers = re.findall(r"\b(\d{1,3})\b", text)
        if numbers:
            valid_nums = [float(n) for n in numbers if 0 <= float(n) <= 100]
            if valid_nums:
                for num in valid_nums:
                    if num > 5: return num
                return valid_nums[-1]
        return None
