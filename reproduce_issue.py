from chatbot_engine import MuseumChatbot

bot = MuseumChatbot()
state = {}
resp, state = bot.process_message("What is fossils", state)
print(f"\nQUERY: What is fossils")
print(f"RESPONSE: {resp}")
print(f"STATE: {state}")
