from chatbot_engine import MuseumChatbot

def test_language_switch():
    bot = MuseumChatbot()
    state = {}
    
    print("Step 1: Asking in Hindi")
    resp1, state = bot.process_message("नमस्ते, मुझे टिकट चाहिए", state)
    print(f"Bot Response 1: {resp1}")
    print(f"Locked Lang: {state.get('locked_lang')}")
    
    print("\nStep 2: Asking in English")
    resp2, state = bot.process_message("What are the museum hours?", state)
    print(f"Bot Response 2: {resp2}")
    print(f"Locked Lang: {state.get('locked_lang')}")

if __name__ == "__main__":
    test_language_switch()
