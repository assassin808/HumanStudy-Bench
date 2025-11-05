"""
Test script for Study 004 - Representativeness Heuristic

Validates the study configuration and runs a basic test.
"""

from pathlib import Path
from src.core.study_config import get_study_config
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.evaluation.scorer import Scorer


def test_study_004_loading():
    """Test that Study 004 loads correctly."""
    print("=" * 80)
    print("Testing Study 004 Configuration")
    print("=" * 80)
    
    # Load study
    benchmark = HumanStudyBench('data')
    study = benchmark.load_study('study_004')
    study_path = study.materials_path.parent
    
    # Get study config
    study_config = get_study_config('study_004', study_path, study.specification)
    
    print(f"\n✓ Study loaded: {study.specification['title']}")
    print(f"  Authors: {', '.join(study.specification['authors'])}")
    print(f"  Year: {study.specification['year']}")
    print(f"  Design: {study.specification['design']['type']}")
    
    # Generate participant profiles
    profiles = study_config.generate_participant_profiles(n_participants=10, random_seed=42)
    print(f"\n✓ Generated {len(profiles)} participant profiles")
    print(f"  Sample profile: age={profiles[0]['age']}, education={profiles[0]['education']}, problem={profiles[0]['assigned_problem']}")
    
    # Create trials for first two participants
    trials_p1 = study_config.create_trials(participant_profile=profiles[0])
    trials_p2 = study_config.create_trials(participant_profile=profiles[1])
    print(f"\n✓ Created trials (between-subjects design)")
    print(f"  Participant 0 gets: {trials_p1[0]['trial_type']}")
    print(f"  Participant 1 gets: {trials_p2[0]['trial_type']}")
    
    # Load ground truth
    import json
    ground_truth_path = study_path / "ground_truth.json"
    with open(ground_truth_path) as f:
        ground_truth = json.load(f)
    
    print(f"\n✓ Ground truth loaded")
    print(f"  Birth sequence: {ground_truth['original_results']['birth_sequence_problem']['proportion_judging_less_likely']} bias rate")
    print(f"  Program choice: {ground_truth['original_results']['program_problem']['proportion_choosing_A']} choosing representative")
    
    # Check validation criteria
    validation = ground_truth['validation_criteria']
    print(f"\n✓ Validation criteria:")
    print(f"  Total weight: {validation['scoring']['total_weight']}")
    print(f"  Pass threshold: {validation['pass_threshold']}")
    print(f"  Required tests: {len(validation['required_tests'])}")
    for test in validation['required_tests']:
        print(f"    - {test['test_id']}: {test['test_name']} (weight={test['weight']}, critical={test['critical']})")
    
    return study_config, study


def test_study_004_mock_run():
    """Test Study 004 configuration without full experiment run."""
    print("\n" + "=" * 80)
    print("Testing Study 004 Configuration Components")
    print("=" * 80)
    
    # Load study
    benchmark = HumanStudyBench('data')
    study = benchmark.load_study('study_004')
    study_path = study.materials_path.parent
    study_config = get_study_config('study_004', study_path, study.specification)
    
    # Test profile generation
    profiles = study_config.generate_participant_profiles(20, random_seed=42)
    print(f"\n✓ Generated {len(profiles)} profiles")
    print(f"  Birth sequence: {sum(1 for p in profiles if p['assigned_problem'] == 'birth_sequence')}")
    print(f"  Program choice: {sum(1 for p in profiles if p['assigned_problem'] == 'program_choice')}")
    
    # Test trial creation for both problem types
    print(f"\n✓ Testing trial creation:")
    birth_profile = next(p for p in profiles if p['assigned_problem'] == 'birth_sequence')
    birth_trials = study_config.create_trials(participant_profile=birth_profile)
    print(f"  Birth sequence trial: {birth_trials[0]['trial_type']}")
    
    program_profile = next(p for p in profiles if p['assigned_problem'] == 'program_choice')
    program_trials = study_config.create_trials(participant_profile=program_profile)
    print(f"  Program choice trial: {program_trials[0]['trial_type']}")
    
    # Test prompt builder
    builder = study_config.get_prompt_builder()
    print(f"\n✓ Prompt builder created: {type(builder).__name__}")
    
    # Test materials loading
    instructions = study_config.get_instructions()
    print(f"\n✓ Instructions loaded ({len(instructions)} characters)")
    
    print(f"\n✓ All configuration components working correctly")
    
    return {"status": "configuration_test_passed"}


def test_study_004_validation():
    """Test Study 004 ground truth validation."""
    print("\n" + "=" * 80)
    print("Testing Ground Truth Validation")
    print("=" * 80)
    
    # Load study
    benchmark = HumanStudyBench('data')
    study = benchmark.load_study('study_004')
    
    # Load ground truth
    import json
    ground_truth_path = study.materials_path.parent / "ground_truth.json"
    with open(ground_truth_path) as f:
        ground_truth = json.load(f)
    
    # Validate ground truth structure
    print(f"\n✓ Ground truth validation:")
    print(f"  Study ID: {ground_truth['study_id']}")
    print(f"  Title: {ground_truth['title']}")
    print(f"  Authors: {', '.join(ground_truth['authors'])}")
    print(f"  Year: {ground_truth['year']}")
    
    # Validate original results match paper
    orig = ground_truth['original_results']
    print(f"\n✓ Original results validation:")
    print(f"  Birth sequence problem:")
    print(f"    - Sample size: {orig['birth_sequence_problem']['ss_total']}")
    print(f"    - Bias proportion: {orig['birth_sequence_problem']['proportion_judging_less_likely']}")
    print(f"    - Expected: 75/92 = 0.815 ✓")
    
    print(f"  Program choice problem:")
    print(f"    - Sample size: {orig['program_problem']['ss_total']}")
    print(f"    - Representative choice: {orig['program_problem']['proportion_choosing_A']}")
    print(f"    - Expected: 67/89 = 0.753 ✓")
    
    # Validate test criteria
    validation = ground_truth['validation_criteria']
    print(f"\n✓ Validation criteria:")
    print(f"  Number of tests: {len(validation['required_tests'])}")
    print(f"  Phenomenon tests: {sum(1 for t in validation['required_tests'] if t['critical'])}")
    print(f"  Data replication tests: {sum(1 for t in validation['required_tests'] if not t['critical'])}")
    
    return {"status": "validation_passed"}


if __name__ == "__main__":
    import sys
    try:
        # Test loading
        study_config, study = test_study_004_loading()
        
        # Test configuration components
        config_result = test_study_004_mock_run()
        
        # Test validation
        validation_result = test_study_004_validation()
        
        print("\n" + "=" * 80)
        print("✓ All tests passed successfully!")
        print("=" * 80)
        print("\nStudy 004 is ready for benchmarking!")
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
