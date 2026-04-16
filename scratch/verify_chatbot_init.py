import sys
import os

# Add the current directory to path
sys.path.append(os.getcwd())

from chatbot_engine import MuseumChatbot

print("Instantiating MuseumChatbot...")
chatbot = MuseumChatbot()

if chatbot.model_id:
    print(f"\nSUCCESS: Chatbot initialized with model: {chatbot.model_id}")
else:
    print("\nFAILURE: Chatbot still using fallback mode.")
