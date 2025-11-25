
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("."))

from src.core.experiment_runner import ExperimentRunner
from src.core.study_config import get_study_config
from src.agents.participant_pool import ParticipantPool

def run_debug():
    print("=== Running Study 002 Debug (n=1) ===")
    
    # Initialize
    runner = ExperimentRunner()
    study_config = get_study_config("study_002")
    
    # Generate 1 profile
    profiles = study_config.generate_participant_profiles(n_participants=1)
    print(f"Generated profile for Participant 0: {profiles[0]['condition_map']}")
    
    # Initialize Pool
    pool = ParticipantPool(
        study_config=study_config,
        n_participants=1,
        model="mistralai/mistral-nemo",
        use_real_llm=True,
        profiles=profiles
    )
    
    # Run 1 participant (15 trials)
    print("\n--- Starting Execution ---\n")
    raw_results = runner.run_study(study_config, pool)
    
    print("\n=== RAW LLM OUTPUTS ===")
    
    # Extract and print raw responses
    for p_data in raw_results.get("individual_data", []):
        pid = p_data["participant_id"]
        print(f"\n[Participant {pid}]")
        
        for trial in p_data.get("trial_responses", []):
            q_id = trial.get("question")
            anchor = trial.get("anchor_condition")
            raw_text = trial.get("response_text", "").strip()
            
            print(f"\n>> Question: {q_id} (Anchor: {anchor})")
            print("-" * 40)
            print(raw_text)
            print("-" * 40)
            
            # Verify parsing
            val = study_config._parse_numeric_estimate(raw_text)
            conf = study_config._parse_confidence(raw_text)
            print(f"   Parsed Estimate: {val}")
            print(f"   Parsed Confidence: {conf}")

if __name__ == "__main__":
    run_debug()

