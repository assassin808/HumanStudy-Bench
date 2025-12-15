"""
Run Study 001 (False Consensus Effect) with Real LLM or Simulation.

Usage:
    python run_study_001.py --n-participants 30 --model mistralai/mistral-nemo
"""

import argparse
import json
import time
import os
import random
import numpy as np
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool, LLMParticipantAgent
from src.core.study_config import get_study_config
import src.studies

class MockStudy001Agent(LLMParticipantAgent):
    """
    Mock agent for testing Study 001 pipeline without API keys.
    Simulates False Consensus Effect data.
    """
    def _simulate_response(self, trial_info: dict, context=None) -> tuple:
        profile = self.profile
        scenario = profile.get("assigned_scenario", "unknown")
        
        # Handle Study 2 Full Questionnaire
        if scenario == "study_2_questionnaire_full":
            # Generate JSON list for 34 items
            items = []
            for i in range(1, 35):
                # Random choice A or B
                my_choice = "Option A" if random.random() < 0.5 else "Option B"
                
                # FCE Simulation:
                # If I choose A, I estimate A higher (e.g., 60-80%)
                # If I choose B, I estimate A lower (e.g., 20-40%)
                if my_choice == "Option A":
                    est_a = int(random.gauss(65, 10))
                else:
                    est_a = int(random.gauss(35, 10))
                
                est_a = max(0, min(100, est_a))
                est_b = 100 - est_a
                
                items.append({
                    "id": f"item_{i}",
                    "my_choice": my_choice,
                    "estimate_a": est_a,
                    "estimate_b": est_b
                })
            
            return json.dumps(items), json.dumps(items)
            
        # Handle Study 1 & 3 (Single Scenarios)
        else:
            # Random choice
            choice_idx = 0 if random.random() < 0.5 else 1
            choices = ["Option A", "Option B"]
            choice = choices[choice_idx]
            
            # FCE Simulation
            if choice == "Option A":
                est_a = int(random.gauss(70, 10))
            else:
                est_a = int(random.gauss(40, 10))
            
            est_a = max(0, min(100, est_a))
            
            response_text = f"""
            I would choose {choice}.
            
            Estimates:
            1. Option A: {est_a}%
            2. Option B: {100 - est_a}%
            """
            
            return choice, response_text

def main():
    parser = argparse.ArgumentParser(description="Run Study 001")
    parser.add_argument("--n-participants", type=int, default=504,
                       help="Number of participants (Default: 504, matching original Study 1+2+3)")
    parser.add_argument("--model", type=str, default="mistralai/mistral-nemo",
                       help="Model name")
    parser.add_argument("--mock", action="store_true", 
                       help="Force mock mode even if API key exists")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print(" " * 25 + "Study 001 - False Consensus Effect")
    print("="*80)
    
    # Check API Key
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPENAI_API_KEY')
    use_real_llm = False
    
    if args.mock:
        print("⚠️  Running in MOCK mode (forced).")
    elif api_key:
        print("✓ API Key found. Using REAL LLM.")
        use_real_llm = True
    else:
        print("⚠️  No API Key found. Running in MOCK mode for demonstration.")
    
    # Load Study
    benchmark = HumanStudyBench("data")
    study = benchmark.load_study("study_001")
    
    # Config
    study_path = study.materials_path.parent
    study_config = get_study_config("study_001", study_path, study.specification)
    prompt_builder = study_config.get_prompt_builder()
    
    # Generate Profiles
    print(f"\nGenerating {args.n_participants} profiles...")
    profiles = study_config.generate_participant_profiles(args.n_participants)
    
    # Create Pool
    # If mocking, we need to inject our MockAgent logic. 
    # We can do this by creating the pool and then swapping the class of the agents,
    # or by not using the pool's default init fully.
    # Cleaner way: The ParticipantPool class creates agents. 
    # We'll let it create them, then replace them if we are mocking.
    
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=args.n_participants,
        use_real_llm=use_real_llm,
        model=args.model,
        api_key=api_key,
        profiles=profiles,
        prompt_builder=prompt_builder
    )
    
    if not use_real_llm:
        # Replace agents with Mock Agents
        new_agents = []
        for p in pool.participants:
            mock_agent = MockStudy001Agent(
                participant_id=p.participant_id,
                profile=p.profile,
                use_real_llm=False
            )
            new_agents.append(mock_agent)
        pool.participants = new_agents
        
    # Run Experiment
    print("\nRunning Experiment...")
    trials = study_config.create_trials()
    instructions = "Please complete the following survey." # Simplified instructions
    
    start_time = time.time()
    results = pool.run_experiment(trials, instructions, prompt_builder=prompt_builder)
    elapsed = time.time() - start_time
    print(f"Experiment finished in {elapsed:.2f}s")
    
    # Aggregate
    print("\nAggregating Results...")
    
    # Prepare data for aggregation (convert from Agent format to Config format)
    individual_data = results.get('individual_data', [])
    results_for_aggregation = {'individual_data': []}
    
    for p_data in individual_data:
        # Reconstruct structure expected by aggregate_results
        # aggregate_results expects: { individual_data: [ { profile: ..., responses: [...] } ] }
        
        # The p_data from get_summary() has: participant_id, profile, responses
        # responses has: response, response_text, etc.
        
        results_for_aggregation['individual_data'].append({
            "profile": p_data['profile'],
            "responses": p_data['responses']
        })

    aggregated = study_config.aggregate_results(results_for_aggregation)
    
    # Display Descriptive Stats
    desc_stats = aggregated.get("descriptive_statistics", {})
    print("\n--- Descriptive Statistics ---")
    print(f"Overall Mean FCE Magnitude: {desc_stats.get('overall_mean_fce_magnitude', 0):.2f}")
    
    for key, val in desc_stats.items():
        if isinstance(val, dict) and "fce_magnitude" in val:
            print(f"\nScenario: {key}")
            print(f"  N(Choice A): {val.get('n_choice_a')}, N(Choice B): {val.get('n_choice_b')}")
            print(f"  Est by A: {val.get('mean_estimate_by_a'):.1f}%, Est by B: {val.get('mean_estimate_by_b'):.1f}%")
            print(f"  FCE Magnitude: {val.get('fce_magnitude'):.1f}")
            
    # Scoring
    print("\n--- Scoring ---")
    score = study_config.custom_scoring(aggregated, study.ground_truth)
    print(json.dumps(score, indent=2))
    
    # Save
    output_dir = Path("results/study_001")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "aggregated": aggregated,
            "score": score,
            "metadata": {
                "model": args.model,
                "n": args.n_participants,
                "mock": not use_real_llm
            }
        }, f, indent=2, default=str)
        
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()

