import json
import numpy as np
from scipy import stats

# 1. Load Data
file_path = 'results/full_benchmark_20251126_003039.json'
print(f"Loading {file_path}...")
with open(file_path, 'r') as f:
    data = json.load(f)

study_data = data['studies'][0] # Assuming Study 001 is the first/only study
individual_data = study_data['individual_data']
desc_stats_json = study_data['descriptive_statistics']
inf_stats_json = study_data['inferential_statistics']

print(f"Loaded Study: {study_data['study_id']}")
print(f"Total Participants: {len(individual_data)}")

# 2. Helper function to extract estimates
# Returns: {scenario_id: {'A': [estimates], 'B': [estimates]}}
def extract_estimates(individual_data):
    extracted = {}
    
    for p in individual_data:
        # Handle single choice scenario (Study 1 & 3)
        if p['profile']['task_type'] in ['story', 'sign']:
            scenario = p['profile']['assigned_scenario']
            response = p['responses'][0]
            choice = response['response'] # "A" or "B"
            
            # Extract estimate from text (simplified, assuming format "I estimate X%...")
            # But wait, we need to parse the text carefully or rely on previous parsing?
            # The JSON has "response_text" like "I would choose Option A. I estimate 75%..."
            # Let's use regex to parse estimate
            import re
            match = re.search(r'(\d+)(?:%)?', response['response_text'])
            estimate = float(match.group(1)) if match else None
            
            if estimate is not None:
                if scenario not in extracted: extracted[scenario] = {'A': [], 'B': []}
                if choice == 'A':
                    extracted[scenario]['A'].append(estimate)
                elif choice == 'B':
                    extracted[scenario]['B'].append(estimate)
                    
        # Handle full questionnaire (Study 2)
        elif p['profile']['task_type'] == 'questionnaire_full':
            response_json_str = p['responses'][0]['response_text']
            # This is a JSON string inside the JSON
            try:
                items = json.loads(response_json_str)
                for item in items:
                    item_id = "study_2_" + item['id'] # e.g. study_2_item_1
                    choice = "A" if "Option A" in item['my_choice'] else "B"
                    estimate_a = float(item['estimate_a'])
                    
                    if item_id not in extracted: extracted[item_id] = {'A': [], 'B': []}
                    if choice == 'A':
                        extracted[item_id]['A'].append(estimate_a)
                    else:
                        extracted[item_id]['B'].append(estimate_a)
            except:
                print(f"Failed to parse Study 2 response for participant {p['participant_id']}")

    return extracted

# 3. Verify Calculations
print("\n--- Verifying FCE Magnitudes ---")
extracted_data = extract_estimates(individual_data)
discrepancies = []

# Accumulate data for Overall Tests
study_1_a, study_1_b = [], []
study_2_a, study_2_b = [], []
study_3_a, study_3_b = [], []

for scenario, groups in extracted_data.items():
    est_a = groups['A']
    est_b = groups['B']
    
    mean_a = np.mean(est_a) if est_a else 0
    mean_b = np.mean(est_b) if est_b else 0
    fce = mean_a - mean_b
    
    # Check against JSON
    json_stats = desc_stats_json.get(scenario, {})
    json_fce = json_stats.get('fce_magnitude')
    
    if json_fce is not None:
        diff = abs(fce - json_fce)
        if diff > 0.01:
            discrepancies.append(f"{scenario}: Calc={fce:.2f}, JSON={json_fce:.2f}")
    
    # Collect for P-tests
    if "study_1" in scenario:
        study_1_a.extend(est_a)
        study_1_b.extend(est_b)
    elif "study_2" in scenario:
        # For Study 2, FCE is usually calculated per item then averaged, 
        # or pooled t-test. Original paper did per-item.
        # But here we check "study_2_overall_effect" which seems to be 
        # a t-test on the FCE magnitudes of the 34 items against 0?
        # Let's calculate the FCE for this item
        if est_a and est_b:
            study_2_a.append(fce) # Store FCE magnitude
    elif "study_3" in scenario:
        study_3_a.extend(est_a)
        study_3_b.extend(est_b)

if discrepancies:
    print(f"Found {len(discrepancies)} discrepancies in Scenario FCE calculations:")
    for d in discrepancies[:5]: print(d)
else:
    print("All Scenario FCE Magnitudes match exactly.")

print("\n--- Verifying Phenomenon Tests (P1, P2, P3) ---")

# P1: Study 1 Combined (Independent t-test)
t_stat_1, p_val_1 = stats.ttest_ind(study_1_a, study_1_b, equal_var=False) # Welch's t-test
print(f"P1 (Study 1): Calc p={p_val_1:.5f}, JSON p={inf_stats_json['study_1_combined_effect']['p_value']:.5f}")

# P2: Study 2 Overall (One-sample t-test on FCEs > 0)
# The JSON says "t_test_1samp_fce", so it treats the 34 item FCEs as samples
t_stat_2, p_val_2 = stats.ttest_1samp(study_2_a, 0, alternative='greater')
print(f"P2 (Study 2): Calc p={p_val_2:.5f}, JSON p={inf_stats_json['study_2_overall_effect']['p_value']:.5f}")

# P3: Study 3 Combined (Independent t-test)
t_stat_3, p_val_3 = stats.ttest_ind(study_3_a, study_3_b, equal_var=False)
print(f"P3 (Study 3): Calc p={p_val_3:.5f}, JSON p={inf_stats_json['study_3_combined_effect']['p_value']:.5f}")

print("\n--- Verifying Data Tests (D1, D2, D3) ---")
# D1: Study 1 Mean FCE
mean_fce_1 = desc_stats_json['study_1_mean_fce']
print(f"D1 (Study 1 Mean FCE): {mean_fce_1:.2f} (Target: 17.2)")

# D2: Study 2 Mean FCE
mean_fce_2 = desc_stats_json['study_2_mean_fce']
# Verify manual calc of mean FCE 2
calc_mean_fce_2 = np.mean(study_2_a) if study_2_a else 0
print(f"D2 (Study 2 Mean FCE): {mean_fce_2:.2f} (Calc: {calc_mean_fce_2:.2f}) (Target: 10.5)")

# D3: Study 3 Mean FCE
mean_fce_3 = desc_stats_json['study_3_mean_fce']
print(f"D3 (Study 3 Mean FCE): {mean_fce_3:.2f} (Target: 31.0)")


