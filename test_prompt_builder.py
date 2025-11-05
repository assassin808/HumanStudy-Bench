"""Test Study 004 PromptBuilder"""

from pathlib import Path
from src.core.study_config import get_study_config

# Load study
from src.core.benchmark import HumanStudyBench
benchmark = HumanStudyBench(data_dir="data")
study = benchmark.load_study("study_004")

# Get study config
study_path = study.materials_path.parent
study_config = get_study_config("study_004", study_path, study.specification)

# Get prompt builder
prompt_builder = study_config.get_prompt_builder()

print("=" * 80)
print("TESTING STUDY 004 PROMPT BUILDER")
print("=" * 80)

# Test with birth_sequence
trial_data_birth = {
    "trial_number": 1,
    "participant_profile": {
        "participant_id": 0,
        "assigned_problem": "birth_sequence"
    }
}

prompt_birth = prompt_builder.build_trial_prompt(trial_data_birth)

print("\n🔢 Birth Sequence Prompt:")
print("-" * 80)
print(prompt_birth)
print("-" * 80)
print(f"Length: {len(prompt_birth)} chars")

# Test with program_choice
trial_data_program = {
    "trial_number": 1,
    "participant_profile": {
        "participant_id": 1,
        "assigned_problem": "program_choice"
    }
}

prompt_program = prompt_builder.build_trial_prompt(trial_data_program)

print("\n🎓 Program Choice Prompt:")
print("-" * 80)
print(prompt_program)
print("-" * 80)
print(f"Length: {len(prompt_program)} chars")

print("\n✅ PromptBuilder test complete!")
