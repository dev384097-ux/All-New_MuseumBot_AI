from chatbot_engine import MuseumChatbot
import re

def test_genai_output():
    bot = MuseumChatbot()
    print("Testing 'Fossil fuels ki hunda hai?'")
    resp, state = bot.process_message('Fossil fuels ki hunda hai?', {'state': 'idle'})
    print("Response:", resp)

if __name__ == "__main__":
    test_genai_output()
