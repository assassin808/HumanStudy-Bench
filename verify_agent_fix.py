from src.agents.llm_participant_agent import LLMParticipantAgent

# Mock minimal agent
agent = LLMParticipantAgent(participant_id=1, profile={})

test_cases = [
    ("Estimate: 29,032", "29032"),
    ("Estimate: 2,800", "2800"),
    ("Value: 25", "25"),
    ("Value: 2.5", "2.5"),
    ("Comparison: Higher\nEstimate: 29,032\nConfidence: 7", "29032"),
    ("I choose Option A", "A"), 
    ("Program B", "B")
]

print("Testing LLMParticipantAgent._parse_response...")
for text, expected in test_cases:
    # We need a dummy trial_info
    result = agent._parse_response(text, {})
    status = "PASS" if result == expected else f"FAIL (Expected {expected}, got {result})"
    print(f"Input: {text!r} -> {result!r} [{status}]")

