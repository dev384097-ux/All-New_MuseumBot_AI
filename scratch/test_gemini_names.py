import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_test = [
    'models/gemini-2.0-flash',
    'models/gemini-flash-latest',
    'models/gemini-1.5-flash' # Just in case
]

for model in models_to_test:
    print(f"\n--- Testing Model: {model} ---")
    try:
        response = client.models.generate_content(
            model=model,
            contents="ping",
            config=types.GenerateContentConfig(max_output_tokens=1)
        )
        print(f"SUCCESS!")
    except Exception as e:
        print(f"FAILURE for {model}: {str(e)}")
