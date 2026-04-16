from chatbot_engine import MuseumChatbot
from datetime import date

bot = MuseumChatbot()
state = {'state': 'awaiting_visit_date', 'exhibition': {'title': 'Science Site'}}

# Test "today"
resp, state = bot.process_message("today", state)
print(f"STORED DATE (Today): {state.get('visit_date')}")

# Test "tomorrow"
state = {'state': 'awaiting_visit_date', 'exhibition': {'title': 'Science Site'}}
resp, state = bot.process_message("tomorrow", state)
print(f"STORED DATE (Tomorrow): {state.get('visit_date')}")

# Test "next Sunday"
state = {'state': 'awaiting_visit_date', 'exhibition': {'title': 'Science Site'}}
resp, state = bot.process_message("next sunday", state)
print(f"STORED DATE (Next Sunday): {state.get('visit_date')}")
