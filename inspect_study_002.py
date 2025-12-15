import json
import sys

file_path = 'results/full_benchmark_20251126_162836.json'

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Keys in root: {list(data.keys())}")
    
    if 'studies' in data:
        studies = data['studies']
    else:
        # Maybe it's a dict of study_id -> result directly?
        studies = data
        
    # Look for study_002
    study_002_data = None
    
    if isinstance(studies, dict):
        if 'study_002' in studies:
            study_002_data = studies['study_002']
        else:
            # try searching values if keys aren't IDs
            pass
    elif isinstance(studies, list):
        for s in studies:
            if s.get('study_id') == 'study_002':
                study_002_data = s
                break
    
    if study_002_data:
        print("\n=== Study 002 Summary ===")
        # Print keys to understand structure
        print(f"Keys in study_002: {list(study_002_data.keys())}")
        
        if 'data_result' in study_002_data:
            print("\n--- Data Result ---")
            print(json.dumps(study_002_data['data_result'], indent=2))
            
        if 'analysis' in study_002_data:
             print("\n--- Analysis ---")
             print(json.dumps(study_002_data['analysis'], indent=2))

        # Check for responses to verify extraction
        responses = []
        if 'responses' in study_002_data:
             responses = study_002_data['responses']
        elif 'raw_results' in study_002_data:
             responses = study_002_data['raw_results']
        elif 'individual_data' in study_002_data:
             responses = study_002_data['individual_data']
             
        print(f"\nTotal Responses Found: {len(responses)}")
        
        if len(responses) > 0:
            print("\n--- Sample Responses (First 3) ---")
            # for i, r in enumerate(responses[:3]):
            #     print(f"Response {i+1}:")
            #     # Print relevant fields to check extraction
            #     print(json.dumps(r, indent=2))
                
    else:
        print("Study 002 not found in the results.")

except Exception as e:
    print(f"Error: {e}")

