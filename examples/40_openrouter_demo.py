"""
OpenRouter Demo - Using mistralai/mistral-nemo with HumanStudyBench

This example demonstrates how to use OpenRouter API with the benchmark.
OpenRouter provides access to multiple LLM providers through a unified API.

Setup:
1. Get an API key from https://openrouter.ai/
2. Set environment variable: export OPENROUTER_API_KEY="sk-or-v1-..."
3. Run this script

Default model: mistralai/mistral-nemo (cost-effective and capable)
Other OpenRouter models you can try:
- anthropic/claude-3-sonnet
- google/gemini-pro
- meta-llama/llama-3-70b-instruct
- openai/gpt-4-turbo
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.benchmark import HumanStudyBench
from src.agents.prompt_builder import get_prompt_builder


def main():
    # Set your OpenRouter API key
    # Option 1: Environment variable
    # export OPENROUTER_API_KEY="sk-or-v1-..."
    
    # Option 2: Set it in code (not recommended for production)
    # os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-..."
    
    # Check if API key is set
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not found!")
        print("   Please set your OpenRouter API key:")
        print("   export OPENROUTER_API_KEY='sk-or-v1-...'")
        print("\n   Get your key at: https://openrouter.ai/keys")
        return
    
    print("="*70)
    print("OpenRouter Demo - mistralai/mistral-nemo")
    print("="*70)
    
    # Load the benchmark
    print("\n📚 Loading Asch conformity study...")
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    benchmark = HumanStudyBench(data_dir=data_dir)
    study = benchmark.load_study("study_001")
    
    # Get prompt builder for this study
    print("🔧 Creating prompt builder...")
    prompt_builder = get_prompt_builder("study_001")
    
    # Create participant pool
    from src.agents.llm_participant_agent import ParticipantPool
    
    # Run with OpenRouter (mistralai/mistral-nemo is the default)
    print("\n🤖 Running experiment with mistralai/mistral-nemo via OpenRouter...")
    print(f"   API Key: {api_key[:20]}...")
    print(f"   API Base: https://openrouter.ai/api/v1")
    
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=3,  # Small number for demo
        use_real_llm=True,
        model="mistralai/mistral-nemo",  # Default, but explicit here
        api_key=api_key,
        random_seed=42
    )
    
    # Create trials (simplified version for demo)
    trials = []
    for i in range(1, 7):  # 6 trials for quick demo
        is_critical = i > 2  # First 2 neutral, rest critical
        
        trials.append({
            "trial_number": i,
            "study_type": "asch_conformity",
            "trial_type": "critical" if is_critical else "neutral",
            "standard_line_length": 8 + (i % 4),
            "comparison_lines": {"A": 7, "B": 8 + (i % 4), "C": 11},
            "correct_answer": "B",
            "confederate_responses": ["A"] * 6 if is_critical else []
        })
    
    # Use instructions from materials via PromptBuilder
    instructions = prompt_builder.get_instructions()
    
    results = pool.run_experiment(trials, instructions, prompt_builder=prompt_builder)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    conformity_stats = results.get("descriptive_statistics", {}).get("conformity_rate", {}).get("experimental", {})
    
    if conformity_stats:
        print(f"\n📊 Conformity Rate Statistics:")
        print(f"   Mean: {conformity_stats.get('mean', 0)*100:.1f}%")
        print(f"   SD: {conformity_stats.get('sd', 0)*100:.1f}%")
        print(f"   Range: {conformity_stats.get('min', 0)*100:.1f}% - {conformity_stats.get('max', 0)*100:.1f}%")
        print(f"   Never conformed: {conformity_stats.get('never_conformed', 0)} participants")
        print(f"   Always conformed: {conformity_stats.get('always_conformed', 0)} participants")
    
    # Show individual responses
    print(f"\n👥 Individual Participant Responses:")
    for participant_data in results.get("individual_data", [])[:3]:
        pid = participant_data["participant_id"]
        conf_rate = participant_data.get("conformity_rate", 0)
        print(f"   Participant {pid}: {conf_rate*100:.1f}% conformity")
    
    print("\n✅ Demo complete!")
    print("\n💡 Try other OpenRouter models:")
    print("   - anthropic/claude-3-sonnet")
    print("   - google/gemini-pro")
    print("   - meta-llama/llama-3-70b-instruct")
    print("   - openai/gpt-4-turbo")


def try_different_models():
    """Example: Compare multiple models from OpenRouter"""
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not set")
        return
    
    # Models to compare
    models = [
        "mistralai/mistral-nemo",      # Fast, cost-effective
        "anthropic/claude-3-sonnet",   # High quality reasoning
        "google/gemini-pro",            # Google's flagship
    ]
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    benchmark = HumanStudyBench(data_dir=data_dir)
    study = benchmark.load_study("study_001")
    prompt_builder = get_prompt_builder("study_001")
    
    print("\n" + "="*70)
    print("COMPARING MULTIPLE OPENROUTER MODELS")
    print("="*70)
    
    results_by_model = {}
    
    # Create simple trials
    trials = [{
        "trial_number": 1,
        "study_type": "asch_conformity",
        "trial_type": "critical",
        "standard_line_length": 10,
        "comparison_lines": {"A": 8, "B": 10, "C": 12},
        "correct_answer": "B",
        "confederate_responses": ["A"] * 6
    }]
    
    # Use instructions from materials via PromptBuilder
    instructions = prompt_builder.get_instructions()
    
    for model in models:
        print(f"\n🤖 Testing {model}...")
        
        from src.agents.llm_participant_agent import ParticipantPool
        
        pool = ParticipantPool(
            study_specification=study.specification,
            n_participants=5,
            use_real_llm=True,
            model=model,
            api_key=api_key,
            random_seed=42
        )
        
        results = pool.run_experiment(trials, instructions, prompt_builder=prompt_builder)
        
        conformity_rate = results.get("descriptive_statistics", {}).get(
            "conformity_rate", {}
        ).get("experimental", {}).get("mean", 0)
        
        results_by_model[model] = conformity_rate
        print(f"   → Mean conformity: {conformity_rate*100:.1f}%")
    
    # Summary
    print("\n" + "="*70)
    print("MODEL COMPARISON SUMMARY")
    print("="*70)
    for model, rate in results_by_model.items():
        print(f"{model:35s} {rate*100:5.1f}% conformity")


if __name__ == "__main__":
    # Run basic demo
    main()
    
    # Uncomment to compare multiple models (costs more API credits)
    # try_different_models()
