from chatbot_engine import MuseumChatbot
import os

def test_chatbot_query(query, history=None):
    if history is None: history = []
    print(f"\nQUERY: '{query}'")
    bot = MuseumChatbot()
    
    state = {'state': 'idle'}
    try:
        response, updated_state = bot.process_message(query, state, history=history)
        print(f"RESPONSE:\n{response}")
        # Count lines
        lines = [l for l in response.strip().split('\n') if l.strip()]
        print(f"LINE COUNT: {len(lines)}")
        return updated_state
    except Exception as e:
        print(f"FAILED: {e}")
        return None

if __name__ == "__main__":
    # 1. Short Answer Test
    test_chatbot_query("Tell me about Harappan civilization")
    
    # 2. Detailed Answer Test
    test_chatbot_query("Explain Harappan civilization in detail")
    
    # 3. Unrelated Test
    test_chatbot_query("How to make a pizza?")
    
    # 4. Unclear Test (short gibberish)
    test_chatbot_query("asdfghjkl")
