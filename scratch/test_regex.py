import re

def check_greeting(key, text):
    # Regex for space-based or start/end boundaries
    pattern = fr'(^|\s){re.escape(key)}(\s|$)'
    return bool(re.search(pattern, text, re.IGNORECASE))

test_cases = [
    ("नमस्ते", "नमस्ते मित्रो", True),
    ("नमस्ते", "नमस्तेमित्रो", False), # Should fail if glued
    ("sat sri akal", "hey sat sri akal how are you", True),
    ("vanakkam", "vanakkam!", True) # Wait, punctuation!
]

# Note: clean_msg already has punctuation removed [^\w\s].
# So "vanakkam!" becomes "vanakkam".

for key, text, expected in test_cases:
    result = check_greeting(key, text)
    print(f"Key: {key} | Text: {text} | Expected: {expected} | Result: {result}")
