from chatbot_engine import MuseumChatbot
import json
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verify_gemini():
    print("--- Initializing Real AI Museum Curator (Gemini) ---")
    bot = MuseumChatbot()
    
    test_cases = [
        {"msg": "Namaste! What can you tell me about the museum?", "description": "English/Hindi Hybrid"},
        {"msg": "संग्रहालय किस समय बंद होता है?", "description": "Pure Hindi (Closing time)"},
        {"msg": "எனக்கு ஒரு டிக்கெட் வேண்டும்", "description": "Tamil (I want a ticket)"},
        {"msg": "3", "description": "State transition test (Selection)"},
        {"msg": "today", "description": "Today normalization test"},
        {"msg": "2", "description": "State transition test (Count)"}
    ]
    
    state = {'state': 'idle'}
    
    for case in test_cases:
        print(f"\nTEST: {case['description']} ('{case['msg']}')")
        try:
            response, state = bot.process_message(case['msg'], state)
            print(f"AI REPLY: {response}")
            print(f"BOT STATE: {state['state']}")
        except Exception as e:
            print(f"VERIFICATION ERROR: {e}")

if __name__ == "__main__":
    verify_gemini()
