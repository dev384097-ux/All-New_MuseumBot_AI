from chatbot_engine import MuseumChatbot
import re

def test_other_langs():
    bot = MuseumChatbot()
    queries = [
        "mala ticket book karayche ahe",
        "enakku ticket book pannalaam",
        "nanage ticket book madabeku"
    ]
    
    for query in queries:
        clean_msg = re.sub(r'[!?,.;:।॥]', '', query.lower()).strip()
        clean_msg = re.sub(r'\s+', ' ', clean_msg)
        
        user_script_data = bot._detect_script(query)
        user_script, script_name = user_script_data
        
        dominant_lang = bot._detect_dominant_language(clean_msg)
        translated_msg, detected_lang = bot._translate_to_en(query)
        
        current_input_lang = dominant_lang if dominant_lang and user_script == 'latin' else detected_lang
        
        print(f"Query: {query}")
        print(f"  Dominant: {dominant_lang}")
        print(f"  Current Input Lang: {current_input_lang}")
        print("-" * 20)

if __name__ == "__main__":
    test_other_langs()
