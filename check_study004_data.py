import json

data = json.load(open('results/full_benchmark_20251104_161640.json'))
study004 = [s for s in data['studies'] if s['study_id']=='study_004'][0]

print("Study 004 Data Check")
print("="*50)

# Check first participant
p0 = study004['individual_data'][0]
print("\nParticipant 0:")
print(f"  profile keys: {list(p0['profile'].keys())}")
print(f"  assigned_problem: {p0['profile'].get('assigned_problem')}")
print(f"  responses: {len(p0['responses'])}")

if p0['responses']:
    r0 = p0['responses'][0]
    print(f"  response[0] keys: {list(r0.keys())}")
    resp_text = r0.get('response') or r0.get('response_text', 'N/A')
    if resp_text and resp_text != 'N/A':
        print(f"  response text: {str(resp_text)[:100]}")
    else:
        print(f"  response text: {resp_text}")

# Check a few more participants
print("\nFirst 5 participants assigned_problem:")
for i in range(min(5, len(study004['individual_data']))):
    p = study004['individual_data'][i]
    assigned = p['profile'].get('assigned_problem', 'MISSING')
    print(f"  P{i}: {assigned}")

# Check trial_info in detail
print("\nP0 trial_info:")
ti = p0['responses'][0]['trial_info']
print(f"  trial_type: {ti.get('trial_type')}")
print(f"  correct_answer: {ti.get('correct_answer')}")
print(f"  study_type: {ti.get('study_type')}")
print(f"  keys: {list(ti.keys())}")

# Check descriptive stats
print("\nDescriptive Statistics:")
desc = study004['descriptive_statistics']
print(f"  birth_sequence n: {desc['birth_sequence_problem']['n']}")
print(f"  program_problem n: {desc['program_problem']['n']}")
