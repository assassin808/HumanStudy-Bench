"""
Example: Using Prompt Builder to automatically convert study specifications into LLM prompts.

This example demonstrates how the new Prompt Builder system solves the key problem:
"How do I convert specification.json into actual LLM inputs?"

Previously: Users had to manually figure out what to feed LLM agents
Now: Automatic conversion with study-specific prompt templates
"""

from pathlib import Path
from src.agents.prompt_builder import get_prompt_builder
from src.core.benchmark import HumanStudyBench

print("=" * 70)
print("Prompt Builder Example - Automatic Specification → LLM Prompt")
print("=" * 70)

# ==============================================================================
# STEP 1: Load a study
# ==============================================================================
print("\nSTEP 1: Loading Study 001 (Asch Conformity Experiment)")
print("-" * 70)

benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")

print(f"✓ Loaded: {study.metadata['title']}")
print(f"✓ Study type: {study.specification.get('study_type', 'asch_conformity')}")

# ==============================================================================
# STEP 2: Create Prompt Builder
# ==============================================================================
print("\nSTEP 2: Creating Prompt Builder")
print("-" * 70)

builder = get_prompt_builder("study_001", data_dir="data")

print(f"✓ Prompt Builder created")
print(f"✓ Templates loaded from: {builder.prompts_path}")
print(f"✓ System template: {'Found' if builder.system_template else 'Not found'}")
print(f"✓ Trial template: {'Found' if builder.trial_template else 'Not found'}")

# ==============================================================================
# STEP 3: Build System Prompt (Agent's Identity)
# ==============================================================================
print("\nSTEP 3: Building System Prompt (Defines participant identity)")
print("-" * 70)

# Define a participant profile
participant_profile = {
    "age": 19,
    "gender": "male",
    "education": "college student",
    "personality_traits": {
        "conformity_tendency": 0.75,  # High conformity
        "independence": 0.25
    }
}

system_prompt = builder.build_system_prompt(participant_profile)

print("\n[SYSTEM PROMPT PREVIEW - First 500 chars]")
print("-" * 70)
print(system_prompt[:500] + "...\n")

# ==============================================================================
# STEP 4: Build Trial Prompt (Stimulus Presentation)
# ==============================================================================
print("\nSTEP 4: Building Trial Prompt (Presents stimulus + social context)")
print("-" * 70)

# Example trial data (from specification)
trial_data = {
    "trial_number": 7,
    "standard_length": 10,
    "comparison_lines": {
        "A": 8,
        "B": 10,
        "C": 12
    },
    "correct_answer": "B",
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]  # Critical trial!
}

trial_prompt = builder.build_trial_prompt(trial_data)

print("\n[TRIAL PROMPT - Complete]")
print("-" * 70)
print(trial_prompt)

# ==============================================================================
# STEP 5: Get Instructions
# ==============================================================================
print("\nSTEP 5: Getting Experimental Instructions")
print("-" * 70)

instructions = builder.get_instructions()

print("\n[INSTRUCTIONS PREVIEW - First 300 chars]")
print("-" * 70)
print(instructions[:300] + "...\n")

# ==============================================================================
# STEP 6: Complete LLM Input Example
# ==============================================================================
print("\nSTEP 6: Complete LLM API Call Example")
print("-" * 70)

print("""
To use with OpenAI API:

import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instructions},  # First: give instructions
        {"role": "assistant", "content": "Yes, I understand..."},
        {"role": "user", "content": trial_prompt}  # Then: present trial
    ],
    temperature=0.7,
    max_tokens=50
)

answer = response.choices[0].message.content
# Expected: "A" (conforming) or "B" (correct but non-conforming)
""")

# ==============================================================================
# STEP 7: Demonstrate Study 002 (Milgram)
# ==============================================================================
print("\n" + "=" * 70)
print("BONUS: Study 002 (Milgram Obedience Experiment)")
print("=" * 70)

builder2 = get_prompt_builder("study_002", data_dir="data")

participant_profile2 = {
    "age": 35,
    "gender": "male",
    "occupation": "high school teacher",
    "education": "bachelor's degree",
    "personality_traits": {
        "authority_obedience": 0.7,  # Moderate-high obedience
        "empathy": 0.6
    }
}

system_prompt2 = builder2.build_system_prompt(participant_profile2)

print("\n[SYSTEM PROMPT PREVIEW]")
print("-" * 70)
print(system_prompt2[:400] + "...\n")

# Critical moment: 300V shock
trial_data2 = {
    "shock_level": 20,
    "voltage": 300,
    "learner_response_correctness": "Wrong",
    "learner_gave_error": True,
    "previous_hesitation": True,
    "experimenter_prod": "It is absolutely essential that you continue."
}

trial_prompt2 = builder2.build_trial_prompt(trial_data2)

print("\n[TRIAL PROMPT - 300V Critical Moment]")
print("-" * 70)
print(trial_prompt2[:600] + "...\n")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("SUMMARY: What Problem Does This Solve?")
print("=" * 70)

print("""
❌ OLD PROBLEM:
   - Users see specification.json with technical details
   - Don't know how to convert it to LLM prompts
   - Have to manually write prompts for each study
   - Risk of inconsistency and missing context

✅ NEW SOLUTION:
   - Prompt Builder automatically converts specification → prompts
   - Study-specific templates in materials/prompts/ folder
   - Each study defines:
     * system_prompt_template.txt (agent identity)
     * trial_prompt_template.txt (stimulus presentation)
   - Automatic variable substitution from specification
   - Specialized builders for different study types

📝 FOR STUDY CREATORS:
   When adding a new study, create:
   1. data/studies/study_XXX/specification.json (technical design)
   2. data/studies/study_XXX/materials/prompts/system_prompt_template.txt
   3. data/studies/study_XXX/materials/prompts/trial_prompt_template.txt
   
   Then users can automatically generate correct prompts!

🎯 FOR BENCHMARK USERS:
   Just 3 lines:
   
   builder = get_prompt_builder("study_001")
   system_prompt = builder.build_system_prompt(profile)
   trial_prompt = builder.build_trial_prompt(trial_data)
   
   That's it! The builder handles all the complexity.
""")

print("\n" + "=" * 70)
print("Example Complete!")
print("=" * 70)
