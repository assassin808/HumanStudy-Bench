"""
Example: User creates custom LLM agents with specific profiles.

This shows how users can:
1. Define their own participant profiles
2. Create specific types of participants to test
3. Compare different personality types
"""

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import LLMParticipantAgent


def create_custom_participant(
    participant_id: int,
    name: str,
    profile_description: dict,
    custom_system_prompt: str = None
) -> LLMParticipantAgent:
    """
    Create a custom participant with specific characteristics.
    
    Users can define exactly what kind of person they want to test.
    """
    return LLMParticipantAgent(
        participant_id=participant_id,
        profile=profile_description,
        use_real_llm=False,  # Change to True for real LLM
        system_prompt_override=custom_system_prompt
    )


def main():
    print("\n" + "="*70)
    print("Custom Participant Profiles Demo")
    print("="*70)
    
    # Load study
    benchmark = HumanStudyBench("data")
    study = benchmark.load_study("study_001")
    
    # Define different types of participants to test
    participants = []
    
    # Type 1: Independent thinker (low conformity)
    print("\n[Creating Participant 1: Independent Thinker]")
    independent = create_custom_participant(
        participant_id=1,
        name="Independent Thinker",
        profile_description={
            "age": 22,
            "gender": "male",
            "education": "college senior",
            "personality_traits": {
                "conformity_tendency": 0.1,  # Very low
                "independence": 0.9,
                "confidence": 0.85,
                "skepticism": 0.75
            }
        },
        custom_system_prompt="""You are a 22-year-old confident college senior participating in a psychology experiment.

You have a strong independent streak and trust your own judgment. You don't easily follow the crowd and prefer to think for yourself. You're naturally skeptical and question things that don't make sense.

Respond as this person would - confidently stating what you see, even if others disagree."""
    )
    participants.append(("Independent", independent))
    
    # Type 2: Highly conforming (high conformity)
    print("[Creating Participant 2: People Pleaser]")
    conformist = create_custom_participant(
        participant_id=2,
        name="People Pleaser",
        profile_description={
            "age": 19,
            "gender": "female",
            "education": "college freshman",
            "personality_traits": {
                "conformity_tendency": 0.75,  # Very high
                "independence": 0.25,
                "social_anxiety": 0.65,
                "need_for_approval": 0.80
            }
        },
        custom_system_prompt="""You are a 19-year-old college freshman participating in a psychology experiment.

You're new to college and want to fit in. You're somewhat anxious in social situations and don't like standing out. When everyone else agrees on something, you tend to go along, even if you're not 100% sure. You value harmony and don't want to be the odd one out.

Respond as this person would - considerately, trying to match what others are saying."""
    )
    participants.append(("Conformist", conformist))
    
    # Type 3: Moderate (average conformity)
    print("[Creating Participant 3: Average Person]")
    moderate = create_custom_participant(
        participant_id=3,
        name="Average Person",
        profile_description={
            "age": 21,
            "gender": "male",
            "education": "college junior",
            "personality_traits": {
                "conformity_tendency": 0.37,  # Average from original study
                "independence": 0.63,
                "confidence": 0.50,
                "social_awareness": 0.60
            }
        }
    )
    participants.append(("Moderate", moderate))
    
    # Type 4: Analytical thinker
    print("[Creating Participant 4: Analytical Thinker]")
    analytical = create_custom_participant(
        participant_id=4,
        name="Analytical",
        profile_description={
            "age": 23,
            "gender": "female",
            "education": "engineering student",
            "personality_traits": {
                "conformity_tendency": 0.15,
                "independence": 0.85,
                "analytical_thinking": 0.90,
                "detail_oriented": 0.85
            }
        },
        custom_system_prompt="""You are a 23-year-old engineering student participating in a psychology experiment.

You have a highly analytical mind and pay close attention to details. You trust measurements and objective facts. When something doesn't add up, you notice immediately. You're comfortable being right even when others disagree, because you've checked the facts.

Respond as this person would - precisely and based on what you observe."""
    )
    participants.append(("Analytical", analytical))
    
    # Create a simple trial
    print("\n" + "="*70)
    print("Running Critical Trial")
    print("="*70)
    
    critical_trial = {
        "trial_number": 5,
        "study_type": "asch_conformity",
        "trial_type": "critical",
        "standard_line_length": 10,
        "comparison_lines": {"A": 8, "B": 10, "C": 12},
        "correct_answer": "B",
        "confederate_responses": ["A", "A", "A", "A", "A", "A"]  # All wrong!
    }
    
    print("\nTrial Setup:")
    print("  Standard line: 10 inches")
    print("  Comparison A: 8 inches")
    print("  Comparison B: 10 inches ← CORRECT")
    print("  Comparison C: 12 inches")
    print("\n  All 6 other participants said: 'A' (WRONG!)")
    print("\n" + "-"*70)
    
    # Have each participant respond
    print("\nParticipant Responses:\n")
    
    for name, participant in participants:
        response = participant.complete_trial(critical_trial)
        
        choice = response["response"]
        is_correct = response["is_correct"]
        conformed = not is_correct
        
        status = "✅ CORRECT" if is_correct else "❌ CONFORMED"
        print(f"  {name:15} → Answer: {choice}  {status}")
        print(f"      Profile: conformity_tendency = {participant.profile['personality_traits']['conformity_tendency']:.2f}")
        if conformed:
            print(f"      → Went along with the group despite knowing they were wrong")
        else:
            print(f"      → Resisted group pressure and gave the correct answer")
        print()
    
    print("="*70)
    print("\nKey Insights:")
    print("="*70)
    print("""
This demo shows how users can:

1. CREATE CUSTOM PROFILES
   - Define specific personality traits
   - Set conformity tendencies
   - Customize background and characteristics

2. TEST SPECIFIC HYPOTHESES
   - Compare high vs low conformity individuals
   - Test effects of personality traits
   - Examine individual differences

3. USE CUSTOM SYSTEM PROMPTS
   - Override default prompts
   - Give LLM specific personas
   - Control exactly how the "participant" behaves

4. TWO USAGE MODES:

   A) DEFAULT MODE (as shown above):
      - User defines participant profile
      - System constructs "pretend you are..." prompt automatically
      - Based on profile traits (age, gender, personality)
   
   B) CUSTOM PROMPT MODE:
      - User provides full system prompt
      - Complete control over LLM persona
      - Useful for specific research questions

REAL USAGE WITH LLM API:
   - Set use_real_llm=True
   - Provide API key
   - LLM generates authentic human-like responses
   - Each participant responds based on their profile
""")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
