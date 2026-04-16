import sys
import os

# Add the current directory to path
sys.path.append(os.getcwd())

from chatbot_engine import MuseumChatbot

chatbot = MuseumChatbot()

test_cases = [
    ("Sat sri akal", "pa"),
    ("ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "pa"),
    ("Vanakkam!", "ta"),
    ("வணக்கம்", "ta"),
    ("Namaste", "hi"),
    ("नमस्ते", "hi"),
    ("नमस्कार", "hi/mr")
]

with open("scratch/greeting_results.txt", "w", encoding="utf-8") as f:
    for msg, expected_lang in test_cases:
        state = {'state': 'idle'}
        try:
            response, new_state = chatbot.process_message(msg, state)
            f.write(f"INPUT: {msg}\n")
            f.write(f"RESPONSE: {response}\n")
            f.write(f"LOCKED LANG: {new_state.get('locked_lang')}\n")
            f.write("-" * 20 + "\n")
        except Exception as e:
            f.write(f"ERROR on {msg}: {str(e)}\n")

print("Done! Results written to scratch/greeting_results.txt")
