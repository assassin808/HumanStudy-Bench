"""
快速测试 Study 004 - 小样本查看原始响应
"""
import json
from pathlib import Path
from datetime import datetime

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.core.study_config import get_study_config

# Import all study configurations
import src.studies

def main():
    print("\n" + "="*80)
    print("Study 004 - Quick Response Check")
    print("="*80)
    
    # Load study
    benchmark = HumanStudyBench("data")
    study = benchmark.load_study("study_004")
    
    # Small sample: 18 participants (2 per condition)
    n_participants = 18
    
    # Get study config
    study_path = study.materials_path.parent
    study_config = get_study_config("study_004", study_path, study.specification)
    
    # Get prompt builder
    builder = study_config.get_prompt_builder()
    instructions = builder.get_instructions()
    
    # Create trials
    trials = study_config.create_trials()
    
    # Generate profiles
    profiles = study_config.generate_participant_profiles(n_participants, random_seed=42)
    
    # Create participant pool
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=n_participants,
        use_real_llm=True,
        model="mistralai/mistral-nemo",
        random_seed=42,
        num_workers=4,
        profiles=profiles,
        prompt_builder=builder
    )
    
    # Run experiment
    raw_results = pool.run_experiment(trials, instructions, prompt_builder=builder)
    
    # Aggregate results
    results = study_config.aggregate_results(raw_results)
    
    # Display responses by condition
    print("\n" + "="*80)
    print("RESPONSES BY CONDITION")
    print("="*80)
    
    individual_data = raw_results.get("individual_data", [])
    
    # Group by condition
    by_condition = {}
    for participant in individual_data:
        profile = participant.get("profile", {})
        problem = profile.get("assigned_problem", "unknown")
        
        if problem not in by_condition:
            by_condition[problem] = []
        
        responses = participant.get("responses", [])
        if responses:
            response_text = responses[0].get("response", "NO RESPONSE")
            by_condition[problem].append(response_text)
    
    # Display
    for problem in sorted(by_condition.keys()):
        print(f"\n{'='*80}")
        print(f"PROBLEM: {problem}")
        print(f"{'='*80}")
        
        responses = by_condition[problem]
        print(f"Total responses: {len(responses)}")
        
        for i, resp in enumerate(responses, 1):
            print(f"\n[Response {i}]")
            print(f"  {resp}")
    
    # Display aggregated stats
    print("\n" + "="*80)
    print("AGGREGATED STATISTICS")
    print("="*80)
    
    desc_stats = results.get("descriptive_statistics", {})
    for problem, stats in desc_stats.items():
        print(f"\n{problem}:")
        print(f"  n: {stats.get('n')}")
        print(f"  bias_count: {stats.get('bias_count')}")
        print(f"  bias_proportion: {stats.get('bias_proportion', 0):.3f}")
        print(f"  interpretation: {stats.get('interpretation')}")
    
    # Save detailed output
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_participants": n_participants,
        "responses_by_condition": by_condition,
        "descriptive_statistics": desc_stats,
        "inferential_statistics": results.get("inferential_statistics", {})
    }
    
    output_file = Path("results") / "study_004_response_check.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n\nDetailed output saved to: {output_file}")

if __name__ == "__main__":
    main()

