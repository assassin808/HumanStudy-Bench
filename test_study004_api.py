"""
Test Study 004 with Real LLM API
Run representativeness heuristic study with actual language model.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.benchmark import HumanStudyBench
from src.core.study_config import get_study_config
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder
from src.evaluation.scorer import Scorer


def main():
    print("="*70)
    print("Study 004: Representativeness Heuristic - Real LLM Test")
    print("Kahneman & Tversky (1972)")
    print("="*70)
    print()
    
    # Check for API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please set it with: export OPENROUTER_API_KEY='your-key-here'")
        return
    
    # Initialize benchmark
    benchmark = HumanStudyBench(data_dir="data")
    
    # Load Study 004
    study = benchmark.load_study("study_004")
    
    print("Study loaded successfully!")
    print(f"Title: {study.metadata['title']}")
    print(f"Authors: {study.metadata['authors'][0]} ({study.metadata['year']})")
    print(f"Design: Between-subjects (birth_sequence vs program_choice)")
    print()
    
    # Get study config
    study_path = study.materials_path.parent
    study_config = get_study_config("study_004", study_path, study.specification)
    
    # Get prompt builder
    builder = get_prompt_builder("study_004")
    instructions = builder.get_instructions()
    
    # Create trials
    trials = study_config.create_trials()
    
    # Generate participant profiles
    n_participants = 10
    profiles = study_config.generate_participant_profiles(n_participants, random_seed=42)
    
    # Run with real LLM
    print(f"Running with {n_participants} participants (5 per problem)...")
    print("Model: mistralai/mistral-nemo (via OpenRouter)")
    print()
    
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=n_participants,
        use_real_llm=True,
        model="mistralai/mistral-nemo",
        api_key=api_key,
        random_seed=42,
        profiles=profiles
    )
    
    results = pool.run_experiment(trials, instructions, prompt_builder=builder)
    
    # Aggregate results
    print("\nAggregating results...")
    results = study_config.aggregate_results(results)
    
    # Evaluate results
    print("Evaluating results...")
    scorer = Scorer()
    evaluation = scorer.evaluate_study(results, study.ground_truth)
    
    # Print results summary
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    if results:
        # Descriptive statistics
        desc_stats = results.get("descriptive_statistics", {})
        print("\nDescriptive Statistics:")
        print("-" * 50)
        
        birth_seq = desc_stats.get("birth_sequence_problem", {})
        print(f"Birth Sequence Problem:")
        print(f"  N: {birth_seq.get('n', 0)}")
        print(f"  Bias Rate: {birth_seq.get('proportion_judging_less_likely', 0):.2%}")
        print(f"  Interpretation: {birth_seq.get('interpretation', 'N/A')}")
        
        program = desc_stats.get("program_problem", {})
        print(f"\nProgram Choice Problem:")
        print(f"  N: {program.get('n', 0)}")
        print(f"  Representative Choice Rate: {program.get('proportion_choosing_representative', 0):.2%}")
        print(f"  Correct Choice Rate: {program.get('proportion_choosing_correct', 0):.2%}")
        print(f"  Interpretation: {program.get('interpretation', 'N/A')}")
        
        # Inferential statistics
        inf_stats = results.get("inferential_statistics", {})
        print("\nInferential Statistics:")
        print("-" * 50)
        
        birth_effect = inf_stats.get("birth_sequence_effect", {})
        print(f"Birth Sequence Effect:")
        print(f"  Z: {birth_effect.get('z_statistic', float('nan')):.3f}")
        print(f"  p: {birth_effect.get('p_value', float('nan')):.4f}")
        print(f"  Significant: {birth_effect.get('significant', False)}")
        print(f"  Conclusion: {birth_effect.get('conclusion', 'N/A')}")
        
        program_effect = inf_stats.get("program_choice_effect", {})
        print(f"\nProgram Choice Effect:")
        print(f"  Z: {program_effect.get('z_statistic', float('nan')):.3f}")
        print(f"  p: {program_effect.get('p_value', float('nan')):.4f}")
        print(f"  Significant: {program_effect.get('significant', False)}")
        print(f"  Conclusion: {program_effect.get('conclusion', 'N/A')}")
        
        # Evaluation scores (from earlier evaluation call)
        evaluation = evaluation or {}
        
        scores = evaluation.get("scores", {})
        for test_name, score in scores.items():
            status = "✅ PASS" if score == 1.0 else "❌ FAIL"
            print(f"  {test_name}: {score:.2f} {status}")
        
        overall = evaluation.get("overall_score", 0)
        print(f"\n  Overall Score: {overall:.1%}")
        
        # Individual responses (first few)
        print("\nSample Responses:")
        print("-" * 50)
        individual_data = results.get("individual_data", [])
        for i, participant in enumerate(individual_data[:3]):  # Show first 3
            profile = participant.get("profile", {})
            problem = profile.get("assigned_problem", "unknown")
            responses = participant.get("responses", [])
            if responses:
                response_text = responses[0].get("response", "N/A")
                print(f"\nParticipant {i} ({problem}):")
                print(f"  Response: {response_text[:100]}...")
    
    print("\n" + "="*70)
    print("Test complete!")
    print("="*70)


if __name__ == "__main__":
    main()
