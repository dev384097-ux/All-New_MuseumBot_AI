import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing API Key: {api_key[:10]}...")

client = genai.Client(api_key=api_key)

models_to_test = [
    'gemini-1.5-flash-8b',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-2.0-flash-exp'
]

for model in models_to_test:
    print(f"\n--- Testing Model: {model} ---")
    try:
        response = client.models.generate_content(
            model=model,
            contents="Hello, say 'connected'",
            config=types.GenerateContentConfig(max_output_tokens=10)
        )
        print(f"SUCCESS: {response.text}")
    except Exception as e:
        print(f"FAILURE for {model}:")
        print(str(e))
        if "401" in str(e):
            print("=> Analysis: Invalid API Key")
        elif "429" in str(e):
            print("=> Analysis: Quota Exhausted / Rate Limit")
        elif "403" in str(e):
            print("=> Analysis: Permission Denied (Region or Key Restriction)")
        elif "404" in str(e):
            print("=> Analysis: Model not found or not in models/ namespace")
        
    time.sleep(1) # Be nice
