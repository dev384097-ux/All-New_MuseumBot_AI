from chatbot_engine import MuseumChatbot
import re
import sys

def test_genai_output():
    # Make sure we print utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    bot = MuseumChatbot()
    print("AI Model initialized?:", bot.model_id)
    
    # Let's bypass try/except and print out what exactly happens
    state = {'state': 'idle', 'locked_lang': 'pa', 'locked_script': 'latin'}
    instructions = bot._get_system_instructions('pa', 'latin')
    prompt = f"SESSION_LANG: pa\nSESSION_SCRIPT: latin\nINSTRUCTIONS: {instructions}\nUSER: Fossil fuels ki hunda hai?"
    
    try:
        response = bot.client.models.generate_content(
            model=bot.model_id,
            contents=prompt,
        )
        print("Raw AI text:", [response.text])
        ai_text = response.text
        # Post processing
        ai_text = re.sub(r'\*\*(.*?)\*\*', r'\1', ai_text)
        ai_text = re.sub(r'__(.*?)__', r'\1', ai_text)
        ai_text = re.sub(r'\*', '', ai_text)
        ai_text = re.sub(r'#+\s*(.*)', r'\1', ai_text)
        print("After regex stripping:", [ai_text])
        
        # Enforce script
        enforced = bot._enforce_script(ai_text, 'latin')
        print("After enforce script:", [enforced])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_genai_output()
