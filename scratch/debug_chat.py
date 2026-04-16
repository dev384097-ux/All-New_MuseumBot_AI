import sys
import os

# Add the current directory to path
sys.path.append(os.getcwd())

from chatbot_engine import MuseumChatbot

chatbot = MuseumChatbot()
state = {'state': 'idle'}
try:
    response, new_state = chatbot.process_message("Book Tickets", state)
    print("RESPONSE:", response)
    print("NEW STATE:", new_state)
except Exception as e:
    import traceback
    print("ERROR DETECTED:")
    traceback.print_exc()
