from chatbot_engine import MuseumChatbot

def test_date_validation():
    bot = MuseumChatbot()
    
    # Mock states
    state_data = {
        'state': 'awaiting_visit_date',
        'locked_lang': 'en',
        'locked_script': 'latin',
        'exhibition': {'title': 'National Museum', 'price': 100}
    }
    
    # Test valid date
    response, new_state = bot.process_message("Tomorrow", state_data.copy())
    print(f"Input: Tomorrow -> Response: {response[:50]}... State: {new_state['state']}")
    
    # Test invalid date (keyword based)
    response, new_state = bot.process_message("yesterday", state_data.copy())
    print(f"Input: yesterday -> Response: {response} State: {new_state['state']}")
    
    # Test another invalid date
    response, new_state = bot.process_message("last week", state_data.copy())
    print(f"Input: last week -> Response: {response} State: {new_state['state']}")

if __name__ == "__main__":
    test_date_validation()
