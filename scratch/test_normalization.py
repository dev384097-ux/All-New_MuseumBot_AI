import re

def test():
    text = "नमस्ते!"
    # Current normalization
    clean_msg = re.sub(r'[^\w\s]', '', text.lower(), flags=re.UNICODE).strip()
    
    native_char = "न"
    is_word = bool(re.match(r'\w', native_char, flags=re.UNICODE))
    
    with open("scratch/norm_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Original: {text}\n")
        f.write(f"Cleaned: '{clean_msg}'\n")
        f.write(f"Cleaned Length: {len(clean_msg)}\n")
        f.write(f"Is Word: {is_word}\n")

test()
