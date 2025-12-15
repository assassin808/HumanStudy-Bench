import re

def test_regex(text):
    print(f"Testing: '{text}'")
    match = re.search(r"Estimate:\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
    if match:
        raw = match.group(1)
        print(f"  Raw match: '{raw}'")
        clean = raw.replace(",", "")
        print(f"  Cleaned: '{clean}'")
        try:
            val = float(clean)
            print(f"  Value: {val}")
        except:
            print("  Float conversion failed")
    else:
        print("  No match found")

texts = [
    "Comparison: Higher\nEstimate: 29,032\nConfidence: 7",
    "Comparison: Higher\nEstimate: 2,800\nConfidence: 6",
    "Comparison: Lower\nEstimate: 12,000\nConfidence: 6",
    "Comparison: Higher\nEstimate: 2.7\nConfidence: 7",
    "Estimate: 25"
]

for t in texts:
    test_regex(t)

