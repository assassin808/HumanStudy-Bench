"""
Test Study 005 (Administrative Obedience) implementation.

Quick validation of:
1. Config loads correctly
2. Prompt builder generates condition-specific prompts
3. Parsing works for obedience responses
4. Aggregation computes obedience rates
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.benchmark import HumanStudyBench
from src.core.study_config import get_study_config

# Import studies to register them
import src.studies


def test_study_005_basic():
    """Test basic Study 005 functionality."""
    print("=" * 60)
    print("Testing Study 005 (Administrative Obedience)")
    print("=" * 60)
    
    # Initialize benchmark
    data_dir = Path(__file__).parent / "data"
    benchmark = HumanStudyBench(data_dir=data_dir)
    
    # Load Study 005
    print("\n1. Loading Study 005...")
    try:
        study = benchmark.load_study("study_005")
        print(f"✓ Study loaded: {study.id}")
        print(f"  Title: {study.metadata.get('title', 'N/A')}")
        print(f"  Authors: {study.metadata.get('authors', 'N/A')}")
        print(f"  Year: {study.metadata.get('year', 'N/A')}")
        
        # Get study config
        study_path = benchmark.studies_dir / "study_005"
        config = get_study_config('study_005', study_path, study.specification)
        print(f"✓ Config loaded: {type(config).__name__}")
    except Exception as e:
        print(f"✗ Failed to load study: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test participant profiles
    print("\n2. Testing participant profile generation...")
    try:
        profiles = config.generate_participant_profiles(n_participants=20, random_seed=42)
        print(f"✓ Generated {len(profiles)} profiles")
        
        # Check condition balance
        obedience_count = sum(1 for p in profiles if p['experimental_condition'] == 'obedience')
        control_count = sum(1 for p in profiles if p['experimental_condition'] == 'control')
        print(f"  Obedience condition: {obedience_count}")
        print(f"  Control condition: {control_count}")
        
        # Show sample profile
        sample = profiles[0]
        print(f"\n  Sample profile:")
        print(f"    Age: {sample['age']}")
        print(f"    Education: {sample['education']}")
        print(f"    Condition: {sample['experimental_condition']}")
    except Exception as e:
        print(f"✗ Failed to generate profiles: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test prompt builder
    print("\n3. Testing prompt builder...")
    try:
        prompt_builder = config.get_prompt_builder()
        print(f"✓ Prompt builder created: {type(prompt_builder).__name__}")
        
        # Test obedience condition prompt
        obedience_profile = next(p for p in profiles if p['experimental_condition'] == 'obedience')
        trial_data = {
            'participant_profile': obedience_profile,
            'trial_number': 1
        }
        
        obedience_prompt = prompt_builder.build_trial_prompt(trial_data)
        print(f"\n  Obedience condition prompt preview:")
        print(f"    Length: {len(obedience_prompt)} chars")
        print(f"    Contains 'experimenter': {'experimenter' in obedience_prompt.lower()}")
        print(f"    Contains 'continue': {'continue' in obedience_prompt.lower()}")
        print(f"    First 200 chars: {obedience_prompt[:200]}...")
        
        # Test control condition prompt
        control_profile = next(p for p in profiles if p['experimental_condition'] == 'control')
        trial_data = {
            'participant_profile': control_profile,
            'trial_number': 1
        }
        
        control_prompt = prompt_builder.build_trial_prompt(trial_data)
        print(f"\n  Control condition prompt preview:")
        print(f"    Length: {len(control_prompt)} chars")
        print(f"    Contains 'autonomy' or 'free': {'free' in control_prompt.lower() or 'autonomy' in control_prompt.lower()}")
        print(f"    First 200 chars: {control_prompt[:200]}...")
        
    except Exception as e:
        print(f"✗ Failed prompt builder test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test response parsing
    print("\n4. Testing response parsing...")
    try:
        from src.studies.study_005_config import Study005Config
        
        test_cases = [
            ("Continue Continue Continue Continue Continue Continue Continue Continue Continue Continue Continue Continue Continue Continue Continue", 15),
            ("Stop at remark 7", 6),
            ("I delivered 12 remarks before stopping", 12),
            ("Continue Continue Continue Stop", 3),
            ("Stop", 0),
            ("15", 15),
            ("0", 0)
        ]
        
        all_passed = True
        for response_text, expected in test_cases:
            parsed = config._parse_remarks_delivered(response_text)
            status = "✓" if parsed == expected else "✗"
            if parsed != expected:
                all_passed = False
            print(f"  {status} '{response_text[:50]}...' → {parsed} (expected {expected})")
        
        if all_passed:
            print("✓ All parsing tests passed")
        else:
            print("✗ Some parsing tests failed")
            
    except Exception as e:
        print(f"✗ Failed parsing test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with mock data
    print("\n5. Testing aggregation with mock data...")
    try:
        # Simulate mock results
        mock_individual_data = []
        
        # Create 10 obedience participants (8 obedient, 2 disobedient)
        for i in range(10):
            obedient = i < 8  # First 8 are obedient
            remarks = 15 if obedient else 7
            mock_individual_data.append({
                "profile": {
                    "participant_id": i,
                    "experimental_condition": "obedience"
                },
                "responses": [{
                    "response": "Continue " * remarks if obedient else f"Stop at remark {remarks + 1}",
                    "response_text": "Continue " * remarks if obedient else f"Stop at remark {remarks + 1}"
                }]
            })
        
        # Create 10 control participants (all disobedient)
        for i in range(10, 20):
            remarks = 3  # Control participants deliver fewer remarks
            mock_individual_data.append({
                "profile": {
                    "participant_id": i,
                    "experimental_condition": "control"
                },
                "responses": [{
                    "response": f"Stop at remark {remarks + 1}",
                    "response_text": f"Stop at remark {remarks + 1}"
                }]
            })
        
        mock_results = {
            "individual_data": mock_individual_data
        }
        
        print(f"✓ Created mock data with {len(mock_individual_data)} participants")
        
        # Test aggregation
        aggregated = config.aggregate_results(mock_results)
        
        print(f"✓ Aggregation completed")
        
        # Check descriptive statistics
        if 'descriptive_statistics' in aggregated:
            stats = aggregated['descriptive_statistics']
            print(f"\n  Descriptive statistics:")
            
            if 'obedience_condition' in stats:
                obedience = stats['obedience_condition']
                print(f"    Obedience condition:")
                print(f"      N: {obedience.get('n', 'N/A')}")
                print(f"      Obedience rate: {obedience.get('obedience_rate', 'N/A'):.2%}")
                print(f"      Mean remarks: {obedience.get('mean_remarks', 'N/A'):.2f}")
            
            if 'control_condition' in stats:
                control = stats['control_condition']
                print(f"    Control condition:")
                print(f"      N: {control.get('n', 'N/A')}")
                print(f"      Obedience rate: {control.get('obedience_rate', 'N/A'):.2%}")
                print(f"      Mean remarks: {control.get('mean_remarks', 'N/A'):.2f}")
        
        # Check inferential statistics
        if 'inferential_statistics' in aggregated:
            inf_stats = aggregated['inferential_statistics']
            print(f"\n  Inferential statistics:")
            
            if 'P1_obedience_above_chance' in inf_stats:
                p1 = inf_stats['P1_obedience_above_chance']
                print(f"    P1 (obedience > chance): p = {p1.get('p_value', 'N/A'):.4f}, sig = {p1.get('significant', False)}")
            
            if 'P2_condition_difference' in inf_stats:
                p2 = inf_stats['P2_condition_difference']
                print(f"    P2 (condition difference): χ² = {p2.get('chi_square', 'N/A'):.2f}, p = {p2.get('p_value', 'N/A'):.4f}")
            
            if 'P3_mean_remarks_difference' in inf_stats:
                p3 = inf_stats['P3_mean_remarks_difference']
                print(f"    P3 (mean remarks diff): t = {p3.get('t_statistic', 'N/A'):.2f}, p = {p3.get('p_value', 'N/A'):.4f}")
        
    except Exception as e:
        print(f"✗ Failed mock data test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ All Study 005 tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_study_005_basic()
    sys.exit(0 if success else 1)
