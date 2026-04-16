from chatbot_engine import MuseumChatbot
import time

def test_chatbot_context():
    print("Initializing Chatbot...")
    bot = MuseumChatbot()
    
    state = {'state': 'idle', 'locked_lang': 'en', 'locked_script': 'latin'}
    history = []
    
    # Message 1
    msg1 = "Tell me about the National Museum of Science."
    print(f"\nUser: {msg1}")
    start = time.time()
    resp1, state = bot.process_message(msg1, state, history=history)
    end = time.time()
    print(f"Bot: {resp1}")
    print(f"Time: {end - start:.2f}s")
    
    history.append({'role': 'user', 'content': msg1})
    history.append({'role': 'assistant', 'content': resp1})
    
    # Message 2 (Context Dependent)
    msg2 = "What are its timings?"
    print(f"\nUser: {msg2}")
    start = time.time()
    resp2, state = bot.process_message(msg2, state, history=history)
    end = time.time()
    print(f"Bot: {resp2}")
    print(f"Time: {end - start:.2f}s")
    
    # Check if "timings" or "hours" is in response and if it's based on "National Museum"
    if "9:00" in resp2 or "timings" in resp2.lower():
        print("\nSUCCESS: Context maintained.")
    else:
        print("\nFAILURE: Context might be lost.")

    # Message 3 (Multilingual)
    msg3 = "Namaste"
    print(f"\nUser: {msg3}")
    resp3, state = bot.process_message(msg3, state, history=history)
    print(f"Bot: {resp3}")
    
    msg4 = "Aapke pas kaunse ticket hain?" # Hinglish
    print(f"\nUser: {msg4}")
    start = time.time()
    resp4, state = bot.process_message(msg4, state, history=history)
    end = time.time()
    print(f"Bot: {resp4}")
    print(f"Time: {end - start:.2f}s")

if __name__ == "__main__":
    test_chatbot_context()
