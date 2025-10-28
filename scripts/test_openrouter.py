"""
Test OpenRouter Integration

Quick test to verify OpenRouter API support with mistralai/mistral-nemo.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.benchmark import HumanStudyBench
from src.agents.prompt_builder import get_prompt_builder


def test_openrouter_setup():
    """Test 1: Verify OpenRouter setup detection"""
    print("\n" + "="*70)
    print("TEST 1: OpenRouter Setup Detection")
    print("="*70)
    
    from src.agents.llm_participant_agent import LLMParticipantAgent
    
    # Test OpenRouter model detection
    test_profile = {"age": 20, "gender": "male"}
    
    # Should detect as OpenRouter (contains "/")
    agent1 = LLMParticipantAgent(
        participant_id=1,
        profile=test_profile,
        model="mistralai/mistral-nemo",
        api_key="test-key"
    )
    
    assert agent1.is_openrouter == True, "Should detect OpenRouter model"
    assert agent1.api_base == "https://openrouter.ai/api/v1", "Should use OpenRouter base URL"
    print("✓ OpenRouter model detection works")
    
    # Should NOT detect as OpenRouter
    agent2 = LLMParticipantAgent(
        participant_id=2,
        profile=test_profile,
        model="gpt-4",
        api_key="test-key"
    )
    
    assert agent2.is_openrouter == False, "Should not detect OpenRouter for OpenAI model"
    assert agent2.api_base is None, "Should use default OpenAI base"
    print("✓ OpenAI model detection works")
    
    # Test custom api_base override
    agent3 = LLMParticipantAgent(
        participant_id=3,
        profile=test_profile,
        model="custom-model",
        api_key="test-key",
        api_base="https://openrouter.ai/api/v1"
    )
    
    assert agent3.is_openrouter == True, "Should detect OpenRouter via api_base"
    print("✓ Custom api_base detection works")
    
    print("\n✅ All setup detection tests passed!")


def test_default_model():
    """Test 2: Verify default model is mistralai/mistral-nemo"""
    print("\n" + "="*70)
    print("TEST 2: Default Model Configuration")
    print("="*70)
    
    from src.agents.llm_participant_agent import LLMParticipantAgent, ParticipantPool
    
    test_profile = {"age": 20, "gender": "male"}
    
    # Test agent default
    agent = LLMParticipantAgent(
        participant_id=1,
        profile=test_profile,
        api_key="test-key"
    )
    
    assert agent.model == "mistralai/mistral-nemo", f"Agent default should be mistralai/mistral-nemo, got {agent.model}"
    print(f"✓ Agent default model: {agent.model}")
    
    # Test pool default
    test_spec = {
        "participants": {
            "n": 5,
            "age_range": [18, 25],
            "age_mean": 20,
            "gender_distribution": {"male": 50, "female": 50}
        }
    }
    
    pool = ParticipantPool(
        study_specification=test_spec,
        api_key="test-key"
    )
    
    assert pool.model == "mistralai/mistral-nemo", f"Pool default should be mistralai/mistral-nemo, got {pool.model}"
    print(f"✓ ParticipantPool default model: {pool.model}")
    
    print("\n✅ Default model tests passed!")


def test_api_key_detection():
    """Test 3: Verify API key environment variable detection"""
    print("\n" + "="*70)
    print("TEST 3: API Key Detection")
    print("="*70)
    
    from src.agents.llm_participant_agent import LLMParticipantAgent
    
    test_profile = {"age": 20, "gender": "male"}
    
    # Save original env vars
    original_openai = os.environ.get("OPENAI_API_KEY")
    original_openrouter = os.environ.get("OPENROUTER_API_KEY")
    
    try:
        # Test OpenRouter key detection
        os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
        if original_openai:
            del os.environ["OPENAI_API_KEY"]
        
        agent1 = LLMParticipantAgent(
            participant_id=1,
            profile=test_profile,
            model="mistralai/mistral-nemo"
        )
        
        assert agent1.api_key == "test-openrouter-key", "Should use OPENROUTER_API_KEY"
        print("✓ OPENROUTER_API_KEY detection works")
        
        # Test OpenAI key detection
        os.environ["OPENAI_API_KEY"] = "test-openai-key"
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]
        
        agent2 = LLMParticipantAgent(
            participant_id=2,
            profile=test_profile,
            model="gpt-4"
        )
        
        assert agent2.api_key == "test-openai-key", "Should use OPENAI_API_KEY"
        print("✓ OPENAI_API_KEY detection works")
        
        # Test explicit key override
        agent3 = LLMParticipantAgent(
            participant_id=3,
            profile=test_profile,
            model="mistralai/mistral-nemo",
            api_key="explicit-key"
        )
        
        assert agent3.api_key == "explicit-key", "Should use explicit api_key"
        print("✓ Explicit api_key override works")
        
    finally:
        # Restore original env vars
        if original_openai:
            os.environ["OPENAI_API_KEY"] = original_openai
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        if original_openrouter:
            os.environ["OPENROUTER_API_KEY"] = original_openrouter
        elif "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]
    
    print("\n✅ API key detection tests passed!")


def test_integration_with_benchmark():
    """Test 4: Verify integration with HumanStudyBench"""
    print("\n" + "="*70)
    print("TEST 4: Benchmark Integration")
    print("="*70)
    
    # Load benchmark with data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    benchmark = HumanStudyBench(data_dir=data_dir)
    study = benchmark.load_study("study_001")
    
    print("✓ Benchmark loaded")
    
    # Get prompt builder
    prompt_builder = get_prompt_builder("study_001")
    print("✓ Prompt builder created")
    
    # Create participant pool
    from src.agents.llm_participant_agent import ParticipantPool
    
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=3,
        use_real_llm=False,  # Simulation mode
        model="mistralai/mistral-nemo",
        random_seed=42
    )
    
    print("✓ ParticipantPool created")
    
    # Create simple trial for testing
    trials = [{
        "trial_number": 1,
        "study_type": "asch_conformity",
        "trial_type": "critical",
        "standard_line_length": 10,
        "comparison_lines": {"A": 8, "B": 10, "C": 12},
        "correct_answer": "B",
        "confederate_responses": ["A"] * 6
    }]
    
    instructions = "You will see lines and choose which comparison line matches the standard."
    
    # Run experiment
    results = pool.run_experiment(trials, instructions, prompt_builder=prompt_builder)
    
    print("✓ Experiment ran successfully")
    
    # Check results structure
    assert "descriptive_statistics" in results
    assert "individual_data" in results
    print("✓ Results structure correct")
    
    conformity_stats = results.get("descriptive_statistics", {}).get("conformity_rate", {}).get("experimental", {})
    if conformity_stats:
        mean_conformity = conformity_stats.get("mean", 0)
        print(f"✓ Mean conformity rate: {mean_conformity*100:.1f}%")
    
    print("\n✅ Benchmark integration tests passed!")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("OPENROUTER INTEGRATION TESTS")
    print("="*70)
    
    try:
        test_openrouter_setup()
        test_default_model()
        test_api_key_detection()
        test_integration_with_benchmark()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        
        print("\n📝 Summary:")
        print("   ✓ OpenRouter model detection works")
        print("   ✓ Default model is mistralai/mistral-nemo")
        print("   ✓ API key detection works (OPENROUTER_API_KEY)")
        print("   ✓ Integration with HumanStudyBench works")
        print("   ✓ Backward compatibility with OpenAI models maintained")
        
        print("\n🚀 Ready to use OpenRouter!")
        print("   Set your API key: export OPENROUTER_API_KEY='sk-or-v1-...'")
        print("   Run demo: python examples/40_openrouter_demo.py")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
