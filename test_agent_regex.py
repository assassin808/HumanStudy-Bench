import re

def test_regex(text):
    print(f"Testing: '{text}'")
    # Original regex
    # r'\b(\d+(?:\.\d+)?)\b'
    
    # New regex proposal
    # r'\b(\d+(?:,\d+)*(?:\.\d+)?)\b'
    
    match = re.search(r'\b(\d+(?:,\d+)*(?:\.\d+)?)\b', text)
    if match:
        print(f"  Match: '{match.group(1)}'")
    else:
        print("  No match")

texts = [
    "Estimate: 29,032",
    "Estimate: 2,800",
    "Value 25",
    "Value 2.5",
    "I have 1,234,567 apples",
    "Start with 1, then 2", # Should match 1 and 2 separately
]

for t in texts:
    test_regex(t)

