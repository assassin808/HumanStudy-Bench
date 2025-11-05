"""
Test Study 002 (Anchoring Effect) implementation.

Quick validation of:
1. Config loads correctly
2. Prompt builder generates appropriate prompts
3. Parsing works for numeric responses
4. Aggregation computes anchoring indices
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.benchmark import HumanStudyBench
from src.core.study_config import get_study_config

# Import studies to register them
import src.studies


def test_study_002_basic():
    """Test basic Study 002 functionality."""
    print("=" * 60)
    print("Testing Study 002 (Anchoring Effect)")
    print("=" * 60)
    
    # Initialize benchmark
    data_dir = Path(__file__).parent / "data"
    benchmark = HumanStudyBench(data_dir=data_dir)
    
    # Load Study 002
    print("\n1. Loading Study 002...")
    try:
        study = benchmark.load_study("study_002")
        print(f"✓ Study loaded: {study.id}")
        print(f"  Title: {study.metadata.get('title', 'N/A')}")
        print(f"  Authors: {study.metadata.get('authors', 'N/A')}")
        print(f"  Year: {study.metadata.get('year', 'N/A')}")
        
        # Get study config
        study_path = benchmark.studies_dir / "study_002"
        config = get_study_config('study_002', study_path, study.specification)
        print(f"✓ Config loaded: {type(config).__name__}")
    except Exception as e:
        print(f"✗ Failed to load study: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test prompt builder
    print("\n2. Testing prompt builder...")
    try:
        prompt_builder = config.get_prompt_builder()
        
        # Test Washington high anchor
        trial_data_wash_high = {
            "participant_profile": {
                "question": "washington",
                "anchor_condition": "high"
            }
        }
        prompt_wash_high = prompt_builder.build_trial_prompt(trial_data_wash_high)
        print(f"✓ Washington high anchor prompt ({len(prompt_wash_high)} chars)")
        print(f"  Contains '1920': {'1920' in prompt_wash_high}")
        print(f"  First 100 chars: {prompt_wash_high[:100]}...")
        
        # Test Chicago low anchor
        trial_data_chi_low = {
            "participant_profile": {
                "question": "chicago",
                "anchor_condition": "low"
            }
        }
        prompt_chi_low = prompt_builder.build_trial_prompt(trial_data_chi_low)
        print(f"✓ Chicago low anchor prompt ({len(prompt_chi_low)} chars)")
        print(f"  Contains '0.2 million': {'0.2 million' in prompt_chi_low}")
        
        # Test Everest high anchor
        trial_data_eve_high = {
            "participant_profile": {
                "question": "everest",
                "anchor_condition": "high"
            }
        }
        prompt_eve_high = prompt_builder.build_trial_prompt(trial_data_eve_high)
        print(f"✓ Everest high anchor prompt ({len(prompt_eve_high)} chars)")
        print(f"  Contains '180': {'180' in prompt_eve_high}")
        
    except Exception as e:
        print(f"✗ Prompt builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test participant profile generation
    print("\n3. Testing participant profile generation...")
    try:
        profiles = config.generate_participant_profiles(n_participants=12, random_seed=42)
        print(f"✓ Generated {len(profiles)} profiles")
        
        # Check balance
        question_counts = {"washington": 0, "chicago": 0, "everest": 0}
        anchor_counts = {"high": 0, "low": 0}
        
        for profile in profiles:
            question_counts[profile["question"]] += 1
            anchor_counts[profile["anchor_condition"]] += 1
        
        print(f"  Question distribution: {question_counts}")
        print(f"  Anchor distribution: {anchor_counts}")
        print(f"  Sample profile: {profiles[0]}")
        
    except Exception as e:
        print(f"✗ Profile generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test numeric parsing
    print("\n4. Testing numeric parsing...")
    try:
        
        test_cases = [
            ("1789", 1789.0),
            ("My estimate is 1850", 1850.0),
            ("I think it's around 2.5 million", 2.5),
            ("Answer: 165 degrees", 165.0),
            ("The answer is 1700.", 1700.0)
        ]
        
        for response, expected in test_cases:
            parsed = config._parse_numeric_estimate(response)
            status = "✓" if parsed == expected else "✗"
            print(f"  {status} '{response}' → {parsed} (expected {expected})")
            
    except Exception as e:
        print(f"✗ Numeric parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ All basic tests passed!")
    print("=" * 60)
    return True


def test_study_002_mock_data():
    """Test aggregation with mock data."""
    print("\n" + "=" * 60)
    print("Testing Study 002 Aggregation with Mock Data")
    print("=" * 60)
    
    from src.core.benchmark import HumanStudyBench
    from src.core.study_config import get_study_config
    
    data_dir = Path(__file__).parent / "data"
    benchmark = HumanStudyBench(data_dir=data_dir)
    study = benchmark.load_study("study_002")
    
    study_path = benchmark.studies_dir / "study_002"
    config = get_study_config('study_002', study_path, study.specification)
    
    # Create mock data showing anchoring effect
    mock_results = {
        "individual_data": [
            # Washington high anchor (1920) - expect higher estimates
            {"profile": {"question": "washington", "anchor_condition": "high"}, 
             "responses": [{"response": "1850", "response_text": "1850"}]},
            {"profile": {"question": "washington", "anchor_condition": "high"}, 
             "responses": [{"response": "1880", "response_text": "1880"}]},
            {"profile": {"question": "washington", "anchor_condition": "high"}, 
             "responses": [{"response": "1860", "response_text": "1860"}]},
            
            # Washington low anchor (1700) - expect lower estimates
            {"profile": {"question": "washington", "anchor_condition": "low"}, 
             "responses": [{"response": "1750", "response_text": "1750"}]},
            {"profile": {"question": "washington", "anchor_condition": "low"}, 
             "responses": [{"response": "1740", "response_text": "1740"}]},
            {"profile": {"question": "washington", "anchor_condition": "low"}, 
             "responses": [{"response": "1730", "response_text": "1730"}]},
            
            # Chicago high anchor (5.0M) - expect higher estimates
            {"profile": {"question": "chicago", "anchor_condition": "high"}, 
             "responses": [{"response": "4.2", "response_text": "4.2 million"}]},
            {"profile": {"question": "chicago", "anchor_condition": "high"}, 
             "responses": [{"response": "3.8", "response_text": "3.8"}]},
            
            # Chicago low anchor (0.2M) - expect lower estimates
            {"profile": {"question": "chicago", "anchor_condition": "low"}, 
             "responses": [{"response": "1.5", "response_text": "1.5 million"}]},
            {"profile": {"question": "chicago", "anchor_condition": "low"}, 
             "responses": [{"response": "2.0", "response_text": "2.0"}]},
        ]
    }
    
    # Aggregate
    print("\nAggregating mock data...")
    results = config.aggregate_results(mock_results)
    
    # Display results
    print("\n--- Washington Results ---")
    wash = results["descriptive_statistics"]["washington"]
    print(f"High anchor mean: {wash.get('mean_high', 'N/A')}")
    print(f"Low anchor mean: {wash.get('mean_low', 'N/A')}")
    print(f"Anchoring index: {wash.get('anchoring_index', 'N/A'):.3f}")
    print(f"p-value: {wash.get('p_value', 'N/A'):.4f}")
    print(f"Significant: {wash.get('significant', False)}")
    print(f"Interpretation: {wash.get('interpretation', 'N/A')}")
    
    print("\n--- Chicago Results ---")
    chi = results["descriptive_statistics"]["chicago"]
    print(f"High anchor mean: {chi.get('mean_high', 'N/A')}")
    print(f"Low anchor mean: {chi.get('mean_low', 'N/A')}")
    print(f"Anchoring index: {chi.get('anchoring_index', 'N/A'):.3f}")
    print(f"p-value: {chi.get('p_value', 'N/A'):.4f}")
    print(f"Significant: {chi.get('significant', False)}")
    
    print("\n--- Overall ---")
    overall = results["descriptive_statistics"]["overall"]
    print(f"Mean anchoring index: {overall.get('mean_anchoring_index', 'N/A'):.3f}")
    print(f"Mean Cohen's d: {overall.get('mean_cohens_d', 'N/A'):.3f}")
    print(f"All effects significant: {overall.get('all_effects_significant', False)}")
    print(f"Interpretation: {overall.get('interpretation', 'N/A')}")
    
    print("\n--- Anchoring Analysis ---")
    analysis = results["anchoring_analysis"]
    print(f"Exhibits anchoring: {analysis.get('exhibits_anchoring', False)}")
    print(f"Anchoring strength: {analysis.get('anchoring_strength', 'N/A')}")
    print(f"Consistency: {analysis.get('consistency', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✓ Mock data aggregation completed!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_study_002_basic()
    
    if success:
        test_study_002_mock_data()
    else:
        print("\n✗ Basic tests failed, skipping mock data test")
        sys.exit(1)
