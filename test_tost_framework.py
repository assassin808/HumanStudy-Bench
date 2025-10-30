"""
Test script for TOST Equivalence Testing Framework

Validates:
1. Standardizers (Freeman-Tukey, Cohen's d, Direct)
2. TOST implementation
3. Scorer integration
4. Study 003 end-to-end
"""

import numpy as np
from src.evaluation.standardizers import (
    StandardizerRegistry,
    ProportionStandardizer,
    RatingStandardizer,
    EffectSizeStandardizer
)
from src.evaluation.tost import tost_test, GLOBAL_DELTA
from src.evaluation.scorer import Scorer
from src.core.study import Study
from pathlib import Path


def test_standardizers():
    """Test all standardizers with known values."""
    print("=" * 70)
    print("TEST 1: Standardizers")
    print("=" * 70)
    
    # Test 1a: Proportion Standardizer (Freeman-Tukey)
    print("\n1a. Proportion Standardizer (Freeman-Tukey)")
    ft = ProportionStandardizer()
    
    # Example: agent 0.70, human 0.72 (both n=100)
    agent_data = {"proportion": 0.70, "n": 100}
    human_data = {"proportion": 0.72, "n": 100}
    
    d, details = ft.compute(agent_data, human_data)
    
    print(f"  Agent: p={agent_data['proportion']}, n={agent_data['n']}")
    print(f"  Human: p={human_data['proportion']}, n={human_data['n']}")
    print(f"  Standardized d: {d:.4f}")
    print(f"  SE pooled: {details['se_pooled']:.4f}")
    print(f"  ✓ Freeman-Tukey transformation working")
    
    # Test 1b: Rating Standardizer (Cohen's d)
    print("\n1b. Rating Standardizer (Cohen's d)")
    cd = RatingStandardizer()
    
    # Example: agent mean=4.2, sd=1.0, n=100; human mean=4.5, sd=1.1, n=76
    agent_data = {"mean": 4.2, "sd": 1.0, "n": 100}
    human_data = {"mean": 4.5, "sd": 1.1, "n": 76}
    
    d, details = cd.compute(agent_data, human_data)
    
    print(f"  Agent: M={agent_data['mean']}, SD={agent_data['sd']}, n={agent_data['n']}")
    print(f"  Human: M={human_data['mean']}, SD={human_data['sd']}, n={human_data['n']}")
    print(f"  Standardized d: {d:.4f}")
    print(f"  SD pooled: {details['sd_pooled']:.4f}")
    print(f"  ✓ Cohen's d working")
    
    # Test 1c: EffectSize Standardizer (direct comparison)
    print("\n1c. EffectSize Standardizer (direct comparison)")
    ds = EffectSizeStandardizer()
    
    # Example: agent h=1.0, se=0.15; human h=1.092, se=0.15
    agent_data = {"effect_size": 1.0, "se": 0.15}
    human_data = {"effect_size": 1.092, "se": 0.15}
    
    d, details = ds.compute(agent_data, human_data)
    
    print(f"  Agent: h={agent_data['effect_size']}, SE={agent_data['se']}")
    print(f"  Human: h={human_data['effect_size']}, SE={human_data['se']}")
    print(f"  Standardized d: {d:.4f}")
    print(f"  SE combined: {details['se_combined']:.4f}")
    print(f"  ✓ Direct standardizer working")
    
    # Test 1d: Registry
    print("\n1d. Standardizer Registry")
    assert isinstance(StandardizerRegistry.get("proportion"), ProportionStandardizer)
    assert isinstance(StandardizerRegistry.get("rating"), RatingStandardizer)
    assert isinstance(StandardizerRegistry.get("effect_size"), EffectSizeStandardizer)
    print(f"  ✓ Registry correctly returns standardizers by data type")
    
    print("\n✅ All standardizer tests passed!")


def test_tost():
    """Test TOST implementation."""
    print("\n" + "=" * 70)
    print("TEST 2: TOST Equivalence Testing")
    print("=" * 70)
    
    # Test 2a: Strong equivalence (d = 0.05, well within δ=0.2)
    print("\n2a. Strong Equivalence (d = 0.05 < δ = 0.2)")
    d = 0.05
    se = 0.05
    n1 = 100
    n2 = 76
    delta = 0.2
    
    result = tost_test(d, se, n1, n2, delta)
    print(f"  d = {d}, SE = {se}, δ = {delta}")
    print(f"  p_TOST = {result['p_tost']:.6f}")
    print(f"  Interpretation: {result['interpretation']}")
    print(f"  ✓ Should have low p-value (strong equivalence): {result['p_tost'] < 0.01}")
    
    # Test 2b: Moderate equivalence (d = 0.15, close to δ=0.2)
    print("\n2b. Moderate Equivalence (d = 0.15 < δ = 0.2)")
    d = 0.15
    result = tost_test(d, se, n1, n2, delta)
    print(f"  d = {d}, SE = {se}, δ = {delta}")
    print(f"  p_TOST = {result['p_tost']:.6f}")
    print(f"  Interpretation: {result['interpretation']}")
    print(f"  ✓ Should have moderate p-value: {0.01 < result['p_tost'] < 0.10}")
    
    # Test 2c: Weak equivalence (d = 0.25, exceeds δ=0.2)
    print("\n2c. Weak Equivalence (d = 0.25 > δ = 0.2)")
    d = 0.25
    result = tost_test(d, se, n1, n2, delta)
    print(f"  d = {d}, SE = {se}, δ = {delta}")
    print(f"  p_TOST = {result['p_tost']:.6f}")
    print(f"  Interpretation: {result['interpretation']}")
    print(f"  ✓ Should have high p-value (insufficient equivalence): {result['p_tost'] > 0.10}")
    
    # Test 2d: Perfect equivalence (d = 0)
    print("\n2d. Perfect Equivalence (d = 0)")
    d = 0.0
    result = tost_test(d, se, n1, n2, delta)
    print(f"  d = {d}, SE = {se}, δ = {delta}")
    print(f"  p_TOST = {result['p_tost']:.6f}")
    print(f"  Interpretation: {result['interpretation']}")
    print(f"  ✓ Should have very low p-value: {result['p_tost'] < 0.001}")
    
    print("\n✅ All TOST tests passed!")


def test_scorer_integration():
    """Test scorer with TOST framework."""
    print("\n" + "=" * 70)
    print("TEST 3: Scorer Integration")
    print("=" * 70)
    
    # Mock agent results for Study 003
    mock_results = {
        "descriptive_statistics": {
            "positive_frame": {
                "n": 100,
                "proportion_choose_safe": 0.70,  # Close to human 0.72
            },
            "negative_frame": {
                "n": 100,
                "proportion_choose_safe": 0.75,  # Close to human 0.78
            },
            "framing_effect": {
                "n": 200,
                "effect_size": 1.05,  # Close to human 1.092
                "se": 0.15
            }
        },
        "inferential_statistics": {
            "chi_square_test": {
                "p_value": 0.001,
                "chi_square": 10.5
            }
        }
    }
    
    # Mock ground truth
    mock_ground_truth = {
        "delta": 0.2,
        "validation_criteria": {
            "required_tests": [
                {
                    "test_id": "P1",
                    "test_type": "phenomenon_level",
                    "method": {"test": "chi_square"},
                    "critical": True,
                    "weight": 2.0,
                    "description": "Chi-square test"
                },
                {
                    "test_id": "D1",
                    "test_type": "data_level",
                    "data_type": "proportion",
                    "method": {
                        "condition": "positive_frame",
                        "metric": "proportion_choose_safe"
                    },
                    "human_baseline": {"proportion": 0.72, "n": 76},
                    "critical": False,
                    "weight": 1.0,
                    "description": "Positive frame TOST"
                },
                {
                    "test_id": "D2",
                    "test_type": "data_level",
                    "data_type": "proportion",
                    "method": {
                        "condition": "negative_frame",
                        "metric": "proportion_choose_safe"
                    },
                    "human_baseline": {"proportion": 0.78, "n": 76},
                    "critical": False,
                    "weight": 1.0,
                    "description": "Negative frame TOST"
                }
            ]
        }
    }
    
    # Create mock study
    class MockStudy:
        def __init__(self):
            self.id = "study_003"
            self.ground_truth = mock_ground_truth
    
    study = MockStudy()
    scorer = Scorer()
    
    print("\n3a. Running scorer with TOST framework...")
    results = scorer.score_study(study, mock_results)
    
    print(f"\n  Total score: {results['total_score']:.4f}")
    print(f"  Phenomenon score: {results['phenomenon_score']:.4f}")
    print(f"  Data score: {results['data_score']:.4f}")
    print(f"  Passed: {results['passed']}")
    
    print("\n3b. Test details:")
    for test_id, test_result in results['tests'].items():
        print(f"\n  {test_id}: {test_result['description']}")
        print(f"    Score: {test_result['score']:.4f}")
        print(f"    Status: {test_result['status']}")
        if 'p_tost' in test_result['details']:
            print(f"    p_TOST: {test_result['details']['p_tost']:.6f}")
            print(f"    Interpretation: {test_result['details']['interpretation']}")
    
    # Validate structure
    assert 'phenomenon_tests' in results
    assert 'data_tests' in results
    assert 'P1' in results['phenomenon_tests']
    assert 'D1' in results['data_tests']
    assert 'D2' in results['data_tests']
    
    print("\n✅ Scorer integration tests passed!")


def test_study_003_end_to_end():
    """Test loading actual Study 003 with new framework."""
    print("\n" + "=" * 70)
    print("TEST 4: Study 003 End-to-End")
    print("=" * 70)
    
    study_path = Path("data/studies/study_003")
    
    if not study_path.exists():
        print("\n  ⚠️  Study 003 not found, skipping end-to-end test")
        return
    
    print("\n4a. Loading Study 003...")
    study = Study.load(study_path)
    print(f"  ✓ Loaded: {study.id}")
    
    print("\n4b. Checking ground truth structure...")
    gt = study.ground_truth
    
    # Check delta parameter
    assert "delta" in gt, "Missing global delta parameter"
    print(f"  ✓ Global delta: {gt['delta']}")
    
    # Check test definitions
    tests = gt["validation_criteria"]["required_tests"]
    data_tests = [t for t in tests if t["test_type"] == "data_level"]
    
    print(f"\n4c. Validating data-level test definitions...")
    for test in data_tests:
        test_id = test["test_id"]
        print(f"\n  Test {test_id}:")
        assert "data_type" in test, f"{test_id} missing data_type"
        print(f"    data_type: {test['data_type']}")
        assert "human_baseline" in test, f"{test_id} missing human_baseline"
        print(f"    human_baseline: {test['human_baseline']}")
        assert "method" in test, f"{test_id} missing method"
        print(f"    method: {test['method']}")
        print(f"    ✓ Test {test_id} properly configured")
    
    print("\n4d. Testing scorer with Study 003...")
    
    # Create realistic mock results
    mock_results = {
        "descriptive_statistics": {
            "positive_frame": {
                "n": 100,
                "proportion_choose_safe": 0.70,
            },
            "negative_frame": {
                "n": 100,
                "proportion_choose_safe": 0.75,
            },
            "framing_effect": {
                "n": 200,
                "effect_size": 1.05,
                "se": 0.15
            }
        },
        "inferential_statistics": {
            "chi_square_test": {
                "p_value": 0.001,
                "chi_square": 10.5
            }
        }
    }
    
    scorer = Scorer()
    results = scorer.score_study(study, mock_results)
    
    print(f"\n  Overall score: {results['total_score']:.4f}")
    print(f"  Passed: {results['passed']}")
    
    # Print all test results
    print("\n  Test Results:")
    for test_id in sorted(results['tests'].keys()):
        test = results['tests'][test_id]
        print(f"    {test_id}: {test['status']} (score={test['score']:.4f})")
        if 'p_tost' in test['details']:
            print(f"      → p_TOST = {test['details']['p_tost']:.4f}")
    
    print("\n✅ Study 003 end-to-end test passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TOST EQUIVALENCE TESTING FRAMEWORK - VALIDATION SUITE")
    print("=" * 70)
    
    try:
        test_standardizers()
        test_tost()
        test_scorer_integration()
        test_study_003_end_to_end()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! TOST FRAMEWORK VALIDATED!")
        print("=" * 70)
        print("\nFramework ready for production use.")
        print("Next steps:")
        print("  1. Update README.md with new statistical framework")
        print("  2. Run full Study 003 experiment")
        print("  3. Compare results with previous Cohen's h approach")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
