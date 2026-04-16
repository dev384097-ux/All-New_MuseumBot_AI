import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents="What is fossils?",
    )
    print(f"RESPONSE: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
