"""
快速 API 测试 - 使用 3 个参与者和 5 个 trials

验证 OpenRouter API 正常工作
"""

import os
from pathlib import Path

# Load .env
if Path(".env").exists():
    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder
from src.core.study_config import get_study_config
import json


def quick_api_test(study_id="study_001", n_participants=3, n_trials=5, verbose=False):
    """快速 API 测试"""
    
    # Setup logging if verbose
    if verbose:
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
    
    print("="*80)
    print(f"🚀 Quick API Test: {study_id}")
    print(f"   Participants: {n_participants}")
    print(f"   Trials: {n_trials}")
    print(f"   Model: mistralai/mistral-nemo")
    if verbose:
        print(f"   Verbose: ON")
    print("="*80)
    
    # Load study
    benchmark = HumanStudyBench(data_dir="data")
    study = benchmark.load_study(study_id)
    
    print(f"\n📚 Study: {study.metadata['title']}")
    
    # Get config and create trials
    study_path = study.materials_path.parent
    config = get_study_config(study_id, study_path, study.specification)
    trials = config.create_trials()[:n_trials]
    
    print(f"✅ Generated {len(trials)} trials")
    
    # Create prompt builder
    builder = get_prompt_builder(study_id)
    instructions = builder.get_instructions()
    
    print(f"✅ Loaded instructions ({len(instructions)} chars)")
    
    # Create participant pool
    print(f"\n🤖 Creating {n_participants} LLM participants...")
    print(f"   Using real API: OpenRouter")
    print(f"   Model: mistralai/mistral-nemo")
    
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=n_participants,
        use_real_llm=True,
        model="mistralai/mistral-nemo",
        random_seed=42,
        num_workers=min(8, n_participants)
    )
    
    print(f"✅ Participants created")
    
    # Run experiment
    print(f"\n▶️  Running experiment...")
    print(f"   This will make {n_participants * n_trials} API calls")
    
    import time
    start = time.time()
    
    results = pool.run_experiment(trials, instructions, prompt_builder=builder)
    
    elapsed = time.time() - start
    
    # Apply study-specific aggregation
    results = config.aggregate_results(results)
    
    print(f"\n✅ Experiment complete in {elapsed:.1f}s")
    print(f"   API calls: {n_participants * n_trials}")
    print(f"   Avg time per call: {elapsed / (n_participants * n_trials):.2f}s")
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    individual_data = results.get("individual_data", [])
    
    if study_id == "study_001":  # Asch
        conformity_stats = results.get("descriptive_statistics", {}).get(
            "conformity_rate", {}
        ).get("experimental", {})
        
        if conformity_stats:
            print(f"\n📊 Conformity Rate: {conformity_stats.get('mean', 0):.1%}")
            print(f"   SD: {conformity_stats.get('sd', 0):.3f}")
            print(f"   Range: [{conformity_stats.get('min', 0):.1%}, {conformity_stats.get('max', 0):.1%}]")
        
        # Show individual responses
        print(f"\n👥 Individual Participants:")
        for p in individual_data[:5]:  # Show first 5
            conf_rate = p.get('conformity_rate', 0)
            if conf_rate is None:
                conf_rate = 0.0
            print(f"   P{p['participant_id']:02d}: {conf_rate:.1%} conformity")
    
    elif study_id == "study_002":  # Milgram
        shock_stats = results.get("descriptive_statistics", {}).get(
            "shock_level", {}
        ).get("experimental", {})
        
        if shock_stats:
            print(f"\n📊 Mean Max Shock: {shock_stats.get('mean', 0):.1f}")
            print(f"   Obedience Rate: {shock_stats.get('obedience_rate', 0):.1%}")
        
        # Show individual max shocks
        print(f"\n👥 Individual Participants:")
        for p in individual_data[:5]:
            print(f"   P{p['participant_id']:02d}: Stopped at shock level {p.get('max_shock_level', 0)}")
    
    # Show some actual responses
    print(f"\n💬 Sample Responses:")
    raw_responses = results.get("raw_responses", [])
    if raw_responses:
        participant_1 = raw_responses[0][:3]  # First 3 trials of first participant
        for response in participant_1:
            trial_num = response.get("trial_number", "?")
            answer = response.get("response", "?")
            correct = "✅" if response.get("is_correct", False) else "❌"
            print(f"   Trial {trial_num}: {answer} {correct}")
    
    # Save results
    output_file = f"results/quick_api_test_{study_id}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    print("\n" + "="*80)
    print("✅ Quick API Test Complete!")
    print("="*80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick API test with real OpenRouter")
    parser.add_argument("--study", default="study_001", help="Study ID")
    parser.add_argument("--n-participants", type=int, default=3, help="Number of participants")
    parser.add_argument("--n-trials", type=int, default=5, help="Number of trials")
    parser.add_argument("--num-workers", type=int, default=None, help="Number of parallel worker threads to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    
    args = parser.parse_args()
    
    quick_api_test(args.study, args.n_participants, args.n_trials, args.verbose)
