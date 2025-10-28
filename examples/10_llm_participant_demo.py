"""
Example: Running Asch Conformity Experiment with LLM Participant Agents

This demonstrates how users interact with the benchmark:
1. Load the study from literature
2. Create LLM participant agents based on participant profiles
3. Run the experiment
4. Collect and analyze results
"""

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.evaluation.scorer import Scorer


def create_asch_trials() -> list:
    """
    Create 18 trials for Asch conformity experiment.
    
    Returns:
        List of trial specifications
    """
    trials = []
    
    # 2 practice trials (neutral)
    for i in range(1, 3):
        trials.append({
            "trial_number": i,
            "study_type": "asch_conformity",
            "trial_type": "practice",
            "standard_line_length": 8 + i,
            "comparison_lines": {"A": 7, "B": 8 + i, "C": 11},
            "correct_answer": "B",
            "confederate_responses": []  # Everyone gives correct answer
        })
    
    # 6 neutral trials + 12 critical trials
    critical_pattern = [False, False, True, True, False, True, 
                       True, False, True, True, False, True, 
                       True, False, True, True]
    
    for i, is_critical in enumerate(critical_pattern, start=3):
        standard = 8 + (i % 4)
        comparison_a = standard - 2
        comparison_b = standard
        comparison_c = standard + 2
        
        if is_critical:
            # Critical trial: confederates unanimously choose wrong answer
            # Make them choose A (too short) or C (too long)
            wrong_answer = "A" if i % 2 == 0 else "C"
            confederates = [wrong_answer] * 6  # 6 confederates all say the same wrong answer
        else:
            # Neutral trial: no confederates (or they give correct answer)
            confederates = []
        
        trials.append({
            "trial_number": i,
            "study_type": "asch_conformity",
            "trial_type": "critical" if is_critical else "neutral",
            "standard_line_length": standard,
            "comparison_lines": {
                "A": comparison_a,
                "B": comparison_b,
                "C": comparison_c
            },
            "correct_answer": "B",
            "confederate_responses": confederates
        })
    
    return trials


def main():
    print("\n" + "="*70)
    print("LLM Participant Agent Demo - Asch Conformity Experiment")
    print("="*70)
    
    # Step 1: Load study from benchmark
    print("\n[Step 1] Loading study from literature...")
    benchmark = HumanStudyBench("data")
    study = benchmark.load_study("study_001")
    
    print(f"  Study: {study.metadata['title']}")
    print(f"  Author: {study.metadata['authors'][0]} ({study.metadata['year']})")
    print(f"  Domain: {study.metadata['domain']}")
    
    # Show participant profile from literature
    print(f"\n  Participant Profile from Literature:")
    print(f"    - Sample size: {study.specification['participants']['n']}")
    print(f"    - Age range: {study.specification['participants']['age_range']}")
    print(f"    - Age: M={study.specification['participants']['age_mean']}, SD={study.specification['participants']['age_sd']}")
    print(f"    - Gender: {study.specification['participants']['gender_distribution']}")
    print(f"    - Source: {study.specification['participants']['recruitment_source']}")
    
    # Step 2: Create participant pool
    print(f"\n[Step 2] Creating LLM participant agents...")
    print(f"  Using simulated mode (use_real_llm=False)")
    print(f"  In real usage, set use_real_llm=True and provide API key")
    
    # For demo, use smaller sample
    n_participants = 50  # Original study had 50 in experimental group
    
    participant_pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=n_participants,
        use_real_llm=False,  # Set to True for real LLM usage
        model="gpt-4"
    )
    
    print(f"  Created {len(participant_pool.participants)} virtual participants")
    print(f"\n  Sample participant profiles:")
    for i in range(min(3, len(participant_pool.participants))):
        p = participant_pool.participants[i]
        print(f"    Participant {i}: {p.profile['age']}yo {p.profile['gender']}, " 
              f"conformity_tendency={p.profile['personality_traits']['conformity_tendency']:.2f}")
    
    # Step 3: Prepare experimental trials
    print(f"\n[Step 3] Preparing experimental trials...")
    trials = create_asch_trials()
    
    critical_trials = [t for t in trials if t["trial_type"] == "critical"]
    neutral_trials = [t for t in trials if t["trial_type"] in ["neutral", "practice"]]
    
    print(f"  Total trials: {len(trials)}")
    print(f"    - Critical trials: {len(critical_trials)} (confederates give wrong answer)")
    print(f"    - Neutral trials: {len(neutral_trials)} (correct judgment)")
    
    # Get instructions from study materials
    instructions_path = study.materials_path / "instructions.txt"
    with open(instructions_path, 'r') as f:
        instructions = f.read()
    
    # Step 4: Run experiment
    print(f"\n[Step 4] Running experiment...")
    results = participant_pool.run_experiment(trials, instructions)
    
    # Step 5: Display results
    print("="*70)
    print("RESULTS")
    print("="*70)
    
    conformity_stats = results["descriptive_statistics"]["conformity_rate"]["experimental"]
    
    print(f"\nConformity Rate (on critical trials):")
    print(f"  Mean: {conformity_stats['mean']:.1%}")
    print(f"  SD: {conformity_stats['sd']:.3f}")
    print(f"  Range: [{conformity_stats['min']:.1%}, {conformity_stats['max']:.1%}]")
    print(f"  Median: {conformity_stats['median']:.1%}")
    
    print(f"\nIndividual Differences:")
    print(f"  Never conformed: {conformity_stats['never_conformed']} ({conformity_stats['never_conformed']/n_participants:.1%})")
    print(f"  Always conformed: {conformity_stats['always_conformed']} ({conformity_stats['always_conformed']/n_participants:.1%})")
    
    print(f"\n" + "="*70)
    print("COMPARISON TO ORIGINAL STUDY")
    print("="*70)
    
    original_rate = study.ground_truth["original_results"]["descriptive_statistics"]["conformity_by_group"]["experimental_group"]["conformity_rate_mean"]
    original_sd = study.ground_truth["original_results"]["descriptive_statistics"]["conformity_by_group"]["experimental_group"]["conformity_rate_sd"]
    
    print(f"\nOriginal Study (Asch, 1952):")
    print(f"  Conformity Rate: {original_rate:.1%} (SD={original_sd:.3f})")
    print(f"  Never conformed: 26% (13/50)")
    print(f"  Always conformed: 2% (1/50)")
    
    print(f"\nLLM Agent Replication:")
    print(f"  Conformity Rate: {conformity_stats['mean']:.1%} (SD={conformity_stats['sd']:.3f})")
    print(f"  Difference: {(conformity_stats['mean'] - original_rate)*100:+.1f} percentage points")
    
    # Step 6: Evaluate against ground truth
    print(f"\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    
    scorer = Scorer()
    score_result = scorer.score_study(study, results)
    
    print(f"\nTests passed: {sum(1 for t in score_result['tests'].values() if t['status'] == 'PASS')}/{len(score_result['tests'])}")
    print(f"Overall score: {score_result['total_score']:.1%}")
    
    for test_id, test_result in score_result['tests'].items():
        status_symbol = "✅" if test_result['status'] == "PASS" else "❌"
        print(f"  {status_symbol} {test_id}: {test_result['status']} (score: {test_result['score']:.2f})")
    
    # Pass/fail evaluation
    pass_eval = study.evaluate_pass_status(score_result['total_score'])
    print(f"\nGrade: {pass_eval['grade'].upper()}")
    print(f"Status: {'✅ PASSED' if pass_eval['passed'] else '❌ FAILED'}")
    print(f"Threshold: {pass_eval['threshold']:.0%}")
    print(f"Margin: {pass_eval['margin']:+.1%}")
    
    print("\n" + "="*70)
    print("\nTo use real LLM APIs:")
    print("  1. Set environment variable: export OPENAI_API_KEY='your-key'")
    print("  2. Change use_real_llm=True in ParticipantPool initialization")
    print("  3. LLM will generate responses based on participant profiles")
    print("\n" + "="*70 + "\n")
    
    # Save results
    import json
    output_file = "results/llm_participant_demo_results.json"
    with open(output_file, 'w') as f:
        # Convert to serializable format
        save_data = {
            "study_id": study.id,
            "n_participants": n_participants,
            "model": "gpt-4 (simulated)",
            "conformity_rate_mean": conformity_stats['mean'],
            "conformity_rate_sd": conformity_stats['sd'],
            "score": score_result['total_score'],
            "grade": pass_eval['grade'],
            "passed": pass_eval['passed']
        }
        json.dump(save_data, f, indent=2)
    
    print(f"Results saved to: {output_file}\n")


if __name__ == "__main__":
    main()
