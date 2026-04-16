import sys
import io
# Ensure UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chatbot_engine import MuseumChatbot

def verify_dynamic_switching():
    bot = MuseumChatbot()
    state = {}
    
    print("\n--- TEST 1: Greeting Switch ---")
    # Start in English
    resp, state = bot.process_message("Hello!", state)
    print(f"User: Hello! | Bot: {resp} | Lang: {state.get('locked_lang')}")
    
    # Switch to Hindi via Namaste
    resp, state = bot.process_message("Namaste", state)
    print(f"User: Namaste | Bot: {resp} | Lang: {state.get('locked_lang')}")
    if state.get('locked_lang') == 'hi':
        print("PASS: Lang switched to hi")
    else:
        print("FAIL: Lang stayed as", state.get('locked_lang'))

    print("\n--- TEST 2: Keyword Switch (Hours) ---")
    # Ask in Hindi (transliterated)
    resp, state = bot.process_message("Timings kya hain?", state)
    print(f"User: Timings kya hain? | Bot: {resp}")
    if "Monday ko band" in resp:
        print("PASS: Replied in Hindi for hours")
    else:
        print("FAIL: Did not reply in Hindi")

    # Switch to English keyword
    resp, state = bot.process_message("Parking", state)
    print(f"User: Parking | Bot: {resp} | Lang: {state.get('locked_lang')}")
    if "valet parking" in resp and state.get('locked_lang') == 'en':
        print("PASS: Switched to English for Parking")
    else:
        print("FAIL: Stayed in Hindi or wrong response")

    print("\n--- TEST 3: AI Dynamic Logic (if client is available) ---")
    if bot.client and bot.model_id:
        # Switch back to Hindi
        resp, state = bot.process_message("टिकट कितने का है?", state)
        print(f"User: टिकट कितने का है? | Bot: {resp} | Lang: {state.get('locked_lang')}")
        
        # Ask something in English
        resp, state = bot.process_message("Tell me about the exhibits", state)
        print(f"User: Tell me about the exhibits | Bot: {resp} | Lang: {state.get('locked_lang')}")
        # Check if response has English (should be English if switched)
        if any(w in resp.lower() for w in ["exhibit", "collection", "display", "museum"]):
             print("PASS: AI seems to have responded in English")
        else:
             print("FAIL: AI might have stayed in Hindi")
    else:
        print("AI not available, skipping AI test.")

    # TEST 4: English Booking Consistency
    print("\n--- TEST 4: English Booking (No accidental Hindi) ---")
    resp, state = bot.process_message("Book Tickets", state)
    print(f"User: Book Tickets | Bot: {resp[:100]}... | Lang: {state.get('locked_lang')}")
    if "help with tickets" in resp.lower() and state.get('locked_lang') == 'en':
        print("PASS: Book Tickets stayed in English")
    else:
        print("FAIL: Book Tickets switched to Hindi or wrong response")

if __name__ == "__main__":
    verify_dynamic_switching()
