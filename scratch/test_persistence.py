from chatbot_engine import MuseumChatbot
import re
import sys

def test_booking_persistence():
    sys.stdout.reconfigure(encoding='utf-8')
    bot = MuseumChatbot()
    print("Testing booking persistence flow")
    
    state = {'state': 'idle'}
    
    print("\n--- User: Mainu ticket book karni hegi")
    resp, state = bot.process_message('Mainu ticket book karni hegi', state)
    print("Response:", resp)
    print("Locked Lang:", state.get('locked_lang'))
    print("State:", state.get('state'))

    print("\n--- User: 1")
    resp, state = bot.process_message('1', state)
    print("Response:", resp)
    print("Locked Lang:", state.get('locked_lang'))
    print("State:", state.get('state'))

    print("\n--- User: Tomorrow")
    resp, state = bot.process_message('Tomorrow', state)
    print("Response:", resp)
    print("Locked Lang:", state.get('locked_lang'))
    print("State:", state.get('state'))

    print("\n--- User: 1")
    resp, state = bot.process_message('1', state)
    print("Response:", resp)
    print("Locked Lang:", state.get('locked_lang'))
    print("State:", state.get('state'))
    
if __name__ == "__main__":
    test_booking_persistence()
