"""
Debug script to trace what happens during Study 004 execution.
"""

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder
from src.core.study_config import get_study_config

# Load study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_004")

# Get study config
study_path = study.materials_path.parent
study_config = get_study_config("study_004", study_path, study.specification)

# Create trials
trials = study_config.create_trials()
print(f"Created {len(trials)} trials")
print(f"Trial structure: {trials[0]}")

# Generate profiles
profiles = study_config.generate_participant_profiles(n_participants=2, random_seed=99)
print(f"\nGenerated {len(profiles)} profiles:")
for i, p in enumerate(profiles):
    print(f"  P{i}: {p}")

# Create participant pool
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=2,
    use_real_llm=False,  # Mock mode to avoid API calls
    random_seed=99,
    profiles=profiles
)

print(f"\nCreated {len(pool.participants)} participants")
for i, p in enumerate(pool.participants):
    print(f"  P{i} profile: {p.profile}")

# Create prompt builder - use study config's custom builder
builder = study_config.get_prompt_builder()
print(f"Using prompt builder: {type(builder).__name__}")

# Simulate what happens during run_experiment
print("\n" + "="*70)
print("Simulating trial execution:")
print("="*70)

for trial_idx, trial in enumerate(trials[:1]):  # Just first trial
    print(f"\nTrial {trial_idx}:")
    print(f"  Original trial dict: {trial}")
    
    for p_idx, participant in enumerate(pool.participants[:2]):  # Just first 2 participants
        print(f"\n  Participant {p_idx}:")
        print(f"    Profile: {participant.profile}")
        
        # This is what happens in run_experiment (line 797)
        trial_with_profile = {**trial, "participant_profile": participant.profile}
        
        print(f"    trial_with_profile keys: {list(trial_with_profile.keys())}")
        print(f"    participant_profile in trial_with_profile: {trial_with_profile.get('participant_profile')}")
        
        # Call prompt builder
        trial_prompt = builder.build_trial_prompt(trial_with_profile)
        
        print(f"    Generated prompt ({len(trial_prompt)} chars): {trial_prompt[:100]}...")
