import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing available models for your API key...")
try:
    for model in client.models.list():
        # In SDK v2, the model object attributes might be different. 
        # Printing the object dict or common attributes.
        print(f"Name: {model.name}")
except Exception as e:
    import traceback
    traceback.print_exc()
