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
        Design based on Ross et al. (1977):
        - Study 1: 80 participants per scenario (4 scenarios) = 320 total
        - Study 2: 80 participants (Questionnaire)
        - Study 3: 104 participants (52 per scenario)
        Total Original N = 504
        
        This implementation distributes n_participants proportionally to the original study sizes.
        """
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        profiles = []
        
        # Define weights based on original paper counts
        scenario_weights = {
            "study_1_supermarket": 80,
            "study_1_term_paper": 80,
            "study_1_traffic_ticket": 80,
            "study_1_space_program": 80,
            "study_2_questionnaire_full": 80,
            "study_3_sign_joes": 51,
            "study_3_sign_repent": 53
        }
        
        total_weight = sum(scenario_weights.values()) # 504
        
        # Calculate counts for each scenario
        scenario_counts = {}
        current_total = 0
        
        # First pass: floor division
        for scenario, weight in scenario_weights.items():
            count = int(n_participants * weight / total_weight)
            scenario_counts[scenario] = count
            current_total += count
            
        # Second pass: distribute remainder
        remainder = n_participants - current_total
        if remainder > 0:
            # Distribute to scenarios with largest weights first (or just round robin)
            # Here we just add to the first 'remainder' scenarios for simplicity,
            # or we could look at fractional parts for better accuracy.
            # Given the numbers, simple distribution is fine.
            keys = list(scenario_weights.keys())
            for i in range(remainder):
                scenario_counts[keys[i % len(keys)]] += 1
        
        # Generate profiles
        assignments = []
        for scenario, count in scenario_counts.items():
            # Determine task type
            if "study_1" in scenario:
                t_type = "story"
            elif "study_2" in scenario:
                t_type = "questionnaire_full"
            else:
                t_type = "sign"
                
            assignments.extend([{
                "scenario": scenario,
                "type": t_type
            }] * count)
            
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
            
            # Always use full response text for extraction
            resp_text = responses[0].get("response_text", "")
            
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
        
        # Calculate sub-study specific means for validation
        study_1_fces = [descriptive_stats[k]["fce_magnitude"] 
                        for k in descriptive_stats.keys() 
                        if k.startswith("study_1_") and "fce_magnitude" in descriptive_stats[k]]
        study_2_fces = [descriptive_stats[k]["fce_magnitude"] 
                        for k in descriptive_stats.keys() 
                        if k.startswith("study_2_") and "fce_magnitude" in descriptive_stats[k]]
        study_3_fces = [descriptive_stats[k]["fce_magnitude"] 
                        for k in descriptive_stats.keys() 
                        if k.startswith("study_3_") and "fce_magnitude" in descriptive_stats[k]]
        
        study_1_mean_fce = np.mean(study_1_fces) if study_1_fces else 0
        study_2_mean_fce = np.mean(study_2_fces) if study_2_fces else 0
        study_3_mean_fce = np.mean(study_3_fces) if study_3_fces else 0
        
        # --- NEW: Combined Inferential Statistics for P-Tests ---
        
        # 1. Study 1 Combined: Pool all estimates across 4 stories
        # Tests if "Estimates by Choosers of A" differs from "Estimates by Choosers of B" (Main Effect)
        s1_keys = [k for k in results_map.keys() if k in self.study_1_scenarios]
        s1_a_estimates = []
        s1_b_estimates = []
        for k in s1_keys:
            s1_a_estimates.extend(results_map[k]['A'])
            s1_b_estimates.extend(results_map[k]['B'])
            
        if len(s1_a_estimates) > 1 and len(s1_b_estimates) > 1:
            t_stat, p_val = stats.ttest_ind(s1_a_estimates, s1_b_estimates, equal_var=False)
            inferential_stats["study_1_combined_effect"] = {
                "test_type": "t_test_ind_pooled",
                "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0.0,
                "p_value": float(p_val) if not np.isnan(p_val) else 1.0,
                "significant": bool(p_val < 0.05) if not np.isnan(p_val) else False,
                "mean_a": float(np.mean(s1_a_estimates)),
                "mean_b": float(np.mean(s1_b_estimates))
            }
            
        # 2. Study 3 Combined: Pool all estimates across 2 signs
        s3_keys = [k for k in results_map.keys() if k in self.study_3_scenarios]
        s3_a_estimates = []
        s3_b_estimates = []
        for k in s3_keys:
            s3_a_estimates.extend(results_map[k]['A'])
            s3_b_estimates.extend(results_map[k]['B'])
            
        if len(s3_a_estimates) > 1 and len(s3_b_estimates) > 1:
            t_stat, p_val = stats.ttest_ind(s3_a_estimates, s3_b_estimates, equal_var=False)
            inferential_stats["study_3_combined_effect"] = {
                "test_type": "t_test_ind_pooled",
                "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0.0,
                "p_value": float(p_val) if not np.isnan(p_val) else 1.0,
                "significant": bool(p_val < 0.05) if not np.isnan(p_val) else False,
                "mean_a": float(np.mean(s3_a_estimates)),
                "mean_b": float(np.mean(s3_b_estimates))
            }
            
        # 3. Study 2 Combined: One-sample t-test on item FCEs
        # Tests if the mean FCE across 34 items is significantly greater than 0
        # This replicates the finding that "difference... was in the predicted direction for 32 of 34 items"
        s2_keys = [k for k in descriptive_stats.keys() 
                   if k.startswith("study_2_") and isinstance(descriptive_stats[k], dict)]
        s2_fces = [descriptive_stats[k].get("fce_magnitude", 0) for k in s2_keys]
        
        if len(s2_fces) > 1:
            # One-sample t-test against 0 (greater)
            t_stat, p_val = stats.ttest_1samp(s2_fces, 0, alternative='greater')
            inferential_stats["study_2_overall_effect"] = {
                "test_type": "t_test_1samp_fce",
                "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0.0,
                "p_value": float(p_val) if not np.isnan(p_val) else 1.0,
                "significant": bool(p_val < 0.05) if not np.isnan(p_val) else False,
                "mean_fce": float(np.mean(s2_fces))
            }
        
        enhanced_results = {
            **raw_results,
            "descriptive_statistics": {
                **descriptive_stats,
                "overall_mean_fce_magnitude": mean_fce,
                "study_1_mean_fce": study_1_mean_fce,
                "study_2_mean_fce": study_2_mean_fce,
                "study_3_mean_fce": study_3_mean_fce
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
        print(f"DEBUG: Inside custom_scoring")
        inferential_stats = results.get("inferential_statistics", {})
        descriptive_stats = results.get("descriptive_statistics", {})
        print(f"DEBUG: keys in descriptive_stats: {list(descriptive_stats.keys())}")
        
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
        # Exclude summary stats like study_2_mean_fce
        study_2_items = [k for k in descriptive_stats.keys() 
                        if k.startswith("study_2_") and k != "study_2_mean_fce" 
                        and isinstance(descriptive_stats[k], dict)]
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
        """
        Process a single scenario response.
        
        The estimate extracted is always for Option A (as per the prompt format).
        We need to group these estimates by the participant's choice:
        - Group 'A': estimates from people who chose Option A
        - Group 'B': estimates from people who chose Option B
        
        Both groups contain estimates for Option A, allowing us to calculate FCE:
        FCE = mean(estimates from A choosers) - mean(estimates from B choosers)
        """
        if key not in results_map:
            results_map[key] = {'A': [], 'B': []}
            
        choice = self._extract_choice(text)
        estimate_for_option_a = self._extract_estimate(text)
        
        if choice and estimate_for_option_a is not None:
            # Add this person's estimate for Option A to their choice group
            results_map[key][choice].append(estimate_for_option_a)

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
        text_upper = text.upper()
        
        # Strategy 1: Look for the exact format we requested: "My choice: Option X" or "3. My choice: Option X"
        exact_match = re.search(r'(?:3\.\s*)?MY CHOICE:\s*OPTION\s+([AB])', text_upper)
        if exact_match:
            return exact_match.group(1)
        
        # Strategy 2: Look for numbered format "3. Option X" (without "My choice:")
        numbered_match = re.search(r'3\.\s*(?:MY CHOICE:?\s*)?OPTION\s+([AB])', text_upper)
        if numbered_match:
            return numbered_match.group(1)
        
        # Strategy 3: Look for "I would choose Option X" or "I choose Option X"
        choice_match = re.search(r'(?:I WOULD CHOOSE|I CHOOSE)\s+OPTION\s+([AB])', text_upper)
        if choice_match:
            return choice_match.group(1)
        
        # Strategy 4: Look for "choose Option X" pattern (more flexible)
        choose_match = re.search(r'CHOOSE\s+OPTION\s+([AB])', text_upper)
        if choose_match:
            return choose_match.group(1)
        
        # Strategy 5: Fallback - look for standalone "Option A" or "Option B" near end of text
        # (avoid matching the prompt text at the beginning)
        last_500 = text_upper[-500:] if len(text_upper) > 500 else text_upper
        if "OPTION B" in last_500 and "OPTION A" not in last_500:
            return 'B'
        if "OPTION A" in last_500 and "OPTION B" not in last_500:
            return 'A'
        
        return None

    def _extract_estimate(self, text: str) -> Optional[float]:
        """Extract percentage estimate for Option A (for single scenarios)."""
        text_clean = text.replace("\n", " ")
        
        # Strategy 1: Look for exact format "1. Estimate for Option A: XX%"
        exact_match = re.search(r'1\.\s*ESTIMATE FOR OPTION A:\s*(\d+(?:\.\d+)?)\s*%', text_clean.upper())
        if exact_match:
            return float(exact_match.group(1))
        
        # Strategy 2: Look for "2. Estimate for Option A: XX%" (for Study 3 format)
        study3_match = re.search(r'2\.\s*ESTIMATE FOR OPTION A:\s*(\d+(?:\.\d+)?)\s*%', text_clean.upper())
        if study3_match:
            return float(study3_match.group(1))
        
        # Strategy 3: Look for any line starting with "1." followed by a percentage
        line1_match = re.search(r'1\.\s*[^:]*?(\d+(?:\.\d+)?)\s*%', text_clean)
        if line1_match:
            return float(line1_match.group(1))
        
        # Strategy 4: Look for first percentage in the text
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text_clean)
        if matches:
            return float(matches[0])
        
        # Strategy 5: Look for bare numbers (fallback)
        numbers = re.findall(r'\b(\d{1,3})\b', text_clean)
        if numbers:
            valid_nums = [float(n) for n in numbers if 0 <= float(n) <= 100]
            if valid_nums:
                for num in valid_nums:
                    if num > 5: 
                        return num
                return valid_nums[-1]
        
        return None
