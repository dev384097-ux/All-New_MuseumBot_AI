import sys
import io
# Ensure UTF-8 output for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from langdetect import detect, DetectorFactory
import re

DetectorFactory.seed = 0

def detect_dominant_language(text):
    text_lower = text.lower()
    
    # Specific Roman-script overrides (from chatbot_engine.py)
    if any(w in text_lower for w in ["sat sri akal", "sasreakal", "ki hal", "mainu", "chahida", "tuhanu"]): return "pa"
    if any(w in text_lower for w in ["namaste", "namaskar", "kaise", "kya", "hai", "chahiye", "mujhe", "kitna"]): return "hi"
    
    hindi_keywords = ["mujhe", "chahiye", "kitna", "kaise", "kya", "hai", "karna", "ticket", "namaste", "shubh", "mera", "aap", "hu"]
    punjabi_keywords = ["mainu", "chahida", "kithe", "ki", "hal", "tuhanu", "dassiye", "daso", "ticketen", "yatra"]
    
    scores = {
        "hi": sum(1 for w in hindi_keywords if w in text_lower),
        "pa": sum(1 for w in punjabi_keywords if w in text_lower)
    }
    
    if sum(scores.values()) == 0:
        return None
        
    return max(scores, key=scores.get)

test_inputs = [
    "नमस्ते",
    "Namaste",
    "How are you?",
    "सत् श्री अकाल",
    "Sat Sri Akal",
    "வணக்கம்",
    "Ticket kab khulega?",
    "Mainu ticket chahida",
    "Ok",
    "Yes",
    "जी"
]

for t in test_inputs:
    try:
        ld = detect(t)
    except:
        ld = "error"
    dom = detect_dominant_language(t)
    print(f"Input: {t:20} | langdetect: {ld:5} | dominant: {str(dom):5}")
