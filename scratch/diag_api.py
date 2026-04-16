import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time

load_dotenv()

def diagnostic():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"DEBUG: API Key starting with: {api_key[:10] if api_key else 'None'}")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    models = ['gemini-1.5-flash-8b', 'gemini-1.5-flash', 'gemini-2.0-flash']
    
    for model in models:
        try:
            print(f"DEBUG: Attempting smoke test for {model}...")
            response = client.models.generate_content(
                model=model,
                contents="ping",
                config=types.GenerateContentConfig(max_output_tokens=1)
            )
            print(f"SUCCESS: {model} is working!")
            return
        except Exception as e:
            print(f"FAILURE: {model} failed. Error: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    diagnostic()
