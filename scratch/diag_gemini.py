from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing API Key: {api_key}")

models_to_test = ['gemini-2.0-flash', 'gemini-flash-latest', 'gemini-1.5-flash']

for model in models_to_test:
    print(f"\n--- Testing Model: {model} ---")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents='Explain the Nataraja statue in 1 sentence.'
        )
        print(f"SUCCESS with {model}!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"FAILURE with {model}: {e}")
