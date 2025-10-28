#!/usr/bin/env python3
"""
Quick test script to verify the benchmark is set up correctly.
"""

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    try:
        from src.core.benchmark import HumanStudyBench
        from src.core.study import Study
        from src.agents.base_agent import BaseAgent
        from src.agents.llm_participant_agent import LLMParticipantAgent, ParticipantPool
        from src.evaluation.scorer import Scorer
        from src.evaluation.metrics import MetricsCalculator
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_load_benchmark():
    """Test loading the benchmark."""
    print("\nTesting benchmark loading...")
    try:
        from src.core.benchmark import HumanStudyBench
        benchmark = HumanStudyBench(data_dir="data")
        print(f"✓ Benchmark loaded: {benchmark}")
        return True
    except Exception as e:
        print(f"✗ Failed to load benchmark: {e}")
        return False


def test_load_study():
    """Test loading a study."""
    print("\nTesting study loading...")
    try:
        from src.core.benchmark import HumanStudyBench
        benchmark = HumanStudyBench(data_dir="data")
        study = benchmark.load_study("study_001")
        print(f"✓ Study loaded: {study}")
        print(f"  Title: {study.metadata['title']}")
        return True
    except Exception as e:
        print(f"✗ Failed to load study: {e}")
        return False


def test_run_agent():
    """Test running an agent on a study."""
    print("\nTesting agent execution...")
    try:
        from src.core.benchmark import HumanStudyBench
        from src.agents.llm_participant_agent import ParticipantPool
        
        benchmark = HumanStudyBench(data_dir="data")
        study = benchmark.load_study("study_001")
        
        # Create small participant pool for quick test
        pool = ParticipantPool(
            study_specification=study.specification,
            n_participants=5,  # Small number for quick test
            use_real_llm=False  # Simulation mode
        )
        
        # Create simple trials manually
        trials = []
        for i in range(1, 4):  # Just 3 trials for quick test
            trials.append({
                "trial_number": i,
                "study_type": "asch_conformity",
                "trial_type": "critical" if i > 1 else "neutral",
                "standard_line_length": 10,
                "comparison_lines": {"A": 8, "B": 10, "C": 12},
                "correct_answer": "B",
                "confederate_responses": ["A"] * 6 if i > 1 else []
            })
        
        # Simple instructions
        instructions = "Judge which line matches the standard line in length."
        
        results = pool.run_experiment(trials, instructions)
        
        print(f"✓ Agent executed successfully")
        print(f"  Generated results for {len(results['individual_data'])} participants")
        return True
    except Exception as e:
        print(f"✗ Failed to run agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scoring():
    """Test scoring agent results."""
    print("\nTesting scoring...")
    try:
        from src.core.benchmark import HumanStudyBench
        from src.agents.llm_participant_agent import ParticipantPool
        from src.evaluation.scorer import Scorer
        
        benchmark = HumanStudyBench(data_dir="data")
        study = benchmark.load_study("study_001")
        scorer = Scorer()
        
        # Create small participant pool for quick test
        pool = ParticipantPool(
            study_specification=study.specification,
            n_participants=5,
            use_real_llm=False
        )
        
        # Create simple trials
        trials = []
        for i in range(1, 4):
            trials.append({
                "trial_number": i,
                "study_type": "asch_conformity",
                "trial_type": "critical" if i > 1 else "neutral",
                "standard_line_length": 10,
                "comparison_lines": {"A": 8, "B": 10, "C": 12},
                "correct_answer": "B",
                "confederate_responses": ["A"] * 6 if i > 1 else []
            })
        
        instructions = "Judge which line matches the standard line in length."
        results = pool.run_experiment(trials, instructions)
        
        score_report = scorer.score_study(study, results)
        
        print(f"✓ Scoring completed")
        print(f"  Total Score: {score_report['total_score']:.1%}")
        print(f"  Status: {'PASSED' if score_report['passed'] else 'FAILED'}")
        return True
    except Exception as e:
        print(f"✗ Failed to score: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("HumanStudyBench Quick Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_load_benchmark,
        test_load_study,
        test_run_agent,
        test_scoring,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All tests passed! Benchmark is ready to use.")
        print("\nTry running:")
        print("  python examples/10_llm_participant_demo.py")
        print("  python examples/11_custom_profiles.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
