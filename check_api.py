import os
import requests
import json
from dotenv import load_dotenv

def check_gemini_key():
    load_dotenv(override=True)
    key = os.getenv("GEMINI_API_KEY")
    
    print("\n" + "="*60)
    print("      --- MUSEUM BOT AI BRAIN DIAGNOSTIC ---")
    print("="*60)
    
    if not key:
        print("\n[!] CRITICAL: No API Key found in .env file.")
        return

    print(f"\n[1] ANALYZING KEY: {key[:5]}...{key[-5:]}")
    
    if key.startswith("AQ."):
        print("\n[!!!] KEY FORMAT MISMATCH DETECTED")
        print("------------------------------------------------------------")
        print("Your key starts with 'AQ.'. This is a Google Cloud / Vertex AI")
        print("Access Token. It is NOT a standard API Key and will EXPIRE.")
        print("\nACTION REQUIRED:")
        print("1. Go to: https://aistudio.google.com/app/apikey")
        print("2. Sign in with your Google Account.")
        print("3. Click 'Create API key' (blue button).")
        print("4. Copy the NEW key (it will start with 'AIza').")
        print("5. Paste it into your .env file as GEMINI_API_KEY.")
        print("------------------------------------------------------------")
    elif key.startswith("AIza"):
        print("\n[ok] Format looks correct (AIza...). Testing connectivity...")
    else:
        print("\n[?] Unusual key format. Testing anyway...")

    # Test against AI Studio
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = {"contents": [{"parts":[{"text": "Hello"}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("\n[SUCCESS] AI Studio Brain is ONLINE!")
        else:
            print(f"\n[OFFLINE] Error {response.status_code}: {response.reason}")
            if response.status_code == 404:
                print("Tip: This usually means the model ID or the key permissions are wrong.")
    except Exception as e:
        print(f"\n[!] Network Error: {e}")

    print("\n" + "="*60)
    print("      --- DIAGNOSIS COMPLETE ---")
    print("="*60 + "\n")

if __name__ == "__main__":
    check_gemini_key()
