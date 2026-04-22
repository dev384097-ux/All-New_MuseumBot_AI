from google import genai
from google.genai import types
import os
import re
import uuid
import time
from database import get_db_connection
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# For consistent language detection results
DetectorFactory.seed = 0

# Configuration constants
MAX_RETRIES = 2
DEFAULT_RETRY_DELAY = 1.0  # seconds
MAX_TOKENS = 1000
MODEL_PRIORITY = [
    'gemini-1.5-flash',       # Stable, high-speed, high-quota
    'gemini-1.5-pro',         # Highly capable, stable
    'gemini-2.0-flash-exp',   # Experimental 2.0
    'gemini-flash-latest'     # Alias for latest flash
]

class MuseumChatbot:
    def __init__(self):
        """Initializes the chatbot engine with a verified AI model."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model_id = None
        self.booking_marker = "[INIT_BOOKING]"
        self._init_templates()
        
        print(f"INFO: Initializing MuseumChatbot Engine...")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found. Operating in Rule-Based Fallback mode.")
        else:
            self._initialize_ai()
    
    def _init_templates(self):
        """Initializes the static conversational phrases and maps."""
        # Conversational Phrases Library (as suggested by the user)
        self.templates = {
            'greeting': {
                'en': "Hello! How can I help you today?",
                'hi_native': "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
                'hi_latin': "Namaste! Kaise help kar sakta hoon?",
                'ta_native': "வணக்கம்! நான் எப்படி உதவலாம்?",
                'ta_latin': "Vanakkam! Naan eppadi help pannalaam?",
                'pa_native': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
                'pa_latin': "Sat Sri Akal! Tuhadi kiven madad karaan?",
                'bn_native': "নমস্কার! আমি কীভাবে সাহায্য করতে পারি?",
                'bn_latin': "Nomoskar! Ami kivabe help korte pari?",
                'te_native': "నమస్తే! నేను ఎలా సహాయం చేయగలను?",
                'te_latin': "Namaste! Nenu ela help cheyagalanu?",
                'kn_native': "ನಮಸ್ಕಾರ! ನಾನು ಹೇಗೆ సహాయ ಮಾಡಬಹುದು?",
                'kn_latin': "Namaskara! Naanu hege help madabahudu?",
                'ml_native': "നമസ്കാരം! ഞാൻ എങ്ങനെ സഹായിക്കാം?",
                'ml_latin': "Namaskaram! Njan engane help cheyyam?",
                'gu_native': "નમસ્તે! હું તમારી કેવી રીતે મદદ કરી શકું?",
                'gu_latin': "Namaste! Hu tamari kem madad kari saku?",
                'mr_native': "नमस्कार! मी तुम्हाला कशी मदत करू शकतो?",
                'mr_latin': "Namaskar! Mi tumhala kashi madat karu shakto?"
            },
            'booking_start': {
                'en': "I can definitely help with tickets. Reply with the number of your choice of Museum Site:<br>",
                'hi_native': "ज़रूर! किस संग्रहालय के लिए टिकट चाहिए? नंबर दें:<br>",
                'hi_latin': "Zaroor! Kaunse museum ke liye booking karni hai? Number batayein:<br>",
                'ta_native': "நிச்சயமாக டிக்கெட்டுகளுக்கு உதவ முடியும். உங்களுக்கு விருப்பமான எண்ணுடன் பதிலளிக்கவும்:<br>",
                'ta_latin': "Sure! Tickets book panna help pannuven. Choice number-a reply pannunga:<br>",
                'pa_native': "ਬਿਲਕੁਲ ਮੈਂ ਟਿਕਟਾਂ ਵਿੱਚ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਆਪਣੀ ਪਸੰਦ ਦੇ ਨੰਬਰ ਨਾਲ ਜਵਾਬ ਦਿਓ:<br>",
                'pa_latin': "Zaroor! Main tickets ch madad kar sakda haan. Choice number dasso:<br>"
            },
            'ticket_count': {
                'en': "Great choice: {title}. How many tickets would you like to book?",
                'hi_native': "अच्छा चुनाव: {title}। आप कितने टिकट बुक करना चाहते हैं?",
                'hi_latin': "Badhiya choice: {title}! Aap kitne tickets lena chahte ho?",
                'ta_native': "சிறந்த தேர்வு: {title}. உங்களுக்கு எத்தனை டிக்கெட்டுகள் வேண்டும்?",
                'ta_latin': "Nalla choice: {title}. Ungalukku ethana tickets venum?",
                'pa_native': "ਵਧੀਆ ਚੋਣ: {title}। ਤੁਸੀਂ ਕਿੰਨੀਆਂ ਟਿਕਟਾਂ ਬੁੱਕ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
                'pa_latin': "Wadiya choice: {title}. Tusi kinniyan ticktan book karna chaunde ho?"
            },
            'ask_date': {
                'en': "When do you plan to visit {title}? Write date in (DD-MM-YYYY)",
                'hi_native': "आप {title} कब जाना चाहते हैं? कृपया चैटबॉट में तारीख लिखें (DD-MM-YYYY)",
                'hi_latin': "Aap {title} kab visit karna chahte hain? Kripya date (DD-MM-YYYY) format mein enter karein.",
                'ta_native': "நீங்கள் எப்போது {title} செல்ல திட்டமிட்டுள்ளீர்கள்? தேதியை உள்ளிடவும் (DD-MM-YYYY)",
                'ta_latin': "Neenga {title} eppo visit panna plan panreenga? Dayavu seithu date (DD-MM-YYYY) format la type pannunga.",
                'pa_native': "ਤੁਸੀਂ {title} ਕਦੋਂ ਜਾਣ ਦੀ ਯੋਜਨਾ ਬਣਾ ਰਹੇ ਹੋ? ਕਿਰਪਾ ਕਰਕੇ ਮਿਤੀ (DD-MM-YYYY) ਫਾਰਮੈਟ ਵਿੱਚ ਦਰਜ ਕਰੋ।",
                'pa_latin': "Tusi {title} kadon visit karna chaunde ho? Kirpa karke date (DD-MM-YYYY) format vich enter karo."
            },
            'payment_confirm': {
                'en': "Confirming {count} tickets for '{title}'. Total is ₹{total}. Proceed?",
                'hi_native': "क्या मैं '{title}' के लिए {count} टिकट पक्के कर दूँ? कुल ₹{total} है।",
                'hi_latin': "Confirming {count} tickets for '{title}'. Total ₹{total} ho gaya. Chalein aage?",
                'ta_native': "உறுதிப்படுத்துகிறோம் {count} டிக்கெட்டுகள் '{title}' க்காக. மொத்தம் ₹{total}. தொடரலாமா?",
                'ta_latin': "Confirming {count} tickets for '{title}'. Total ₹{total} varudhu. Proceed pannalama?",
                'pa_native': "ਪੁਸ਼ਟੀ ਕਰ ਰਹੇ ਹਾਂ {count} ਟਿਕਟਾਂ '{title}' ਲਈ। ਕੁੱਲ ₹{total} ਹੈ। ਅੱਗੇ ਵਧੀਏ?",
                'pa_latin': "Confirming {count} tickets for '{title}'. Total ₹{total} ho gaya. Agge vadhye?"
            },
            'hours': {
                'en': "Museum Hours: 9:00 AM - 6:00 PM (Tue-Sun). Closed Mondays.",
                'hi_native': "संग्रहालय का समय: सुबह 9:00 - शाम 6:00 (मंगलवार-रविवार)। सोमवार को बंद रहता है।",
                'hi_latin': "Museum timings: 9:00 AM se 6:00 PM (Tue-Sun). Monday ko band rehta hai.",
                'ta_native': "அருங்காட்சியக நேரம்: காலை 9:00 - மாலை 6:00 (செவ்வாய்-ஞாயிறு). திங்கள் கிழமை விடுமுறை.",
                'ta_latin': "Museum timings: 9:00 AM to 6:00 PM (Tue-Sun). Monday leave.",
                'pa_native': "ਅਜਾਇਬ ਘਰ ਦਾ ਸਮਾਂ: ਸਵੇਰੇ 9:00 - ਸ਼ਾਮ 6:00 (ਮੰਗਲਵਾਰ-ਐਤਵਾਰ)। ਸੋਮਵਾਰ ਨੂੰ ਬੰਦ ਰਹਿੰਦਾ ਹੈ।",
                'pa_latin': "Museum timings: 9:00 AM se 6:00 PM (Tue-Sun). Monday band hunda hai."
            },
            'parking': {
                'en': "We have valet parking available in the North Wing. It is free for visitors.",
                'hi_native': "हमारे पास नॉर्थ विंग में वैलेट पार्किंग उपलब्ध है। यह आगंतुकों के लिए निःशुल्क है।",
                'hi_latin': "North Wing mein valet parking available hai. Visitors ke liye ye free hai.",
                'ta_native': "வடக்குப் பகுதியில் வாகன நிறுத்துமிடம் உள்ளது. பார்வையாளர்களுக்கு இது இலவசம்.",
                'ta_latin': "North Wing-la parking facility iruku. Idhu free service.",
                'pa_native': "ਸਾਡੇ ਕੋਲ ਉੱਤਰੀ ਵਿੰਗ ਵਿੱਚ ਪਾਰਕਿੰਗ ਉਪਲਬਧ ਹੈ। ਸੈਲਾਨੀਆਂ ਲਈ ਇਹ ਮੁਫਤ ਹੈ।",
                'pa_latin': "North Wing ch parking available hai. Visitors layi eh free hai."
            },
            'cafe': {
                'en': "The Curator's Cafe is on the 2nd floor, open until 5 PM.",
                'hi_native': "क्यूरेटर का कैफे दूसरी मंजिल पर है, शाम 5 बजे तक खुला रहता है।",
                'hi_latin': "Curator's Cafe 2nd floor par hai, shaam 5 baje tak khula rehta hai.",
                'ta_native': "கியூரேட்டர் உணவகம் 2வது மாடியில் உள்ளது, மாலை 5 மணி வரை திறந்திருக்கும்.",
                'ta_latin': "Curator's Cafe 2nd floor-la iruku, 5 PM varaikkum open-la irukkum.",
                'pa_native': "ਕਿਊਰੇਟਰ ਦਾ ਕੈਫే ਦੂਜੀ ਮੰਜ਼ਿਲ 'ਤੇ ਹੈ, ਸ਼ਾਮ 5 ਵਜੇ ਤੱਕ ਖੁੱਲ੍ਹਾ ਰਹਿੰਦਾ ਹੈ।",
                'pa_latin': "Curator's Cafe 2nd floor te hai, shyam 5 baje tak khulla rehnda hai."
            },
            'security': {
                'en': "Security is our priority with 24/7 CCTV and entry screening.",
                'hi_native': "सुरक्षा हमारी प्राथमिकता है। 24/7 सीसीटीवी और प्रवेश जांच उपलब्ध है।",
                'hi_latin': "Security hamari priority hai. 24/7 CCTV aur screening available hai.",
                'ta_native': "பாதுகாப்பிற்கு முன்னுரிமை அளிக்கப்படுகிறது, 24/7 சிசிடிவி கண்காணிப்பு உள்ளது.",
                'ta_latin': "Security mukkusu. 24/7 CCTV surveillance iruku.",
                'pa_native': "ਸੁਰੱਖਿਆ ਸਾਡੀ ਤਜੀਹ ਹੈ, 24/7 ਸੀਸੀਟੀਵੀ ਨਿਗਰਾਨੀ ਉਪਲਬਧ ਹੈ।",
                'pa_latin': "Security sadi priority hai, 24/7 CCTV surveillance hai."
            },
            'ask_tier': {
                'en': "Please select the ticket type for these {count} tickets:<br>1. Adult (₹{price} each)<br>2. Student / Child (₹{s_price} each)<br>3. Group (5+) (₹{g_price} each)",
                'hi_native': "इन {count} टिकटों के लिए प्रकार चुनें:<br>1. व्यक्ति (₹{price} प्रत्येक)<br>2. छात्र / बच्चा (₹{s_price} प्रत्येक)<br>3. समूह 5+ (₹{g_price} प्रत्येक)",
                'hi_latin': "In {count} tickets ke liye type chunein:<br>1. Adult (₹{price} each)<br>2. Student / Child (₹{s_price} each)<br>3. Group 5+ (₹{g_price} each)",
                'ta_native': "இந்த {count} டிக்கெட்டுகளுக்கான வகையைத் தேர்ந்தெடுக்கவும்:<br>1. பெரியவர் (₹{price})<br>2. மாணவர் / குழந்தை (₹{s_price})<br>3. குழு 5+ (₹{g_price})",
                'ta_latin': "Inidhu {count} tickets-kku type choose pannunga:<br>1. Adult (₹{price})<br>2. Student / Child (₹{s_price})<br>3. Group 5+ (₹{g_price})",
                'pa_native': "ਇਹਨਾਂ {count} ਟਿਕਟਾਂ ਲਈ ਕਿਸਮ ਚੁਣੋ:<br>1. ਬਾਲਗ (₹{price} ਹਰੇਕ)<br>2. ਵਿਦਿਆਰਥੀ / ਬੱਚਾ (₹{s_price} ਹਰੇਕ)<br>3. ਸਮੂਹ 5+ (₹{g_price} ਹਰੇਕ)",
                'pa_latin': "Inna {count} ticktan layi type chuno:<br>1. Adult (₹{price})<br>2. Student / Child (₹{s_price})<br>3. Group 5+ (₹{g_price})"
            },
            'unknown': {
                'en': "Our digital curator is experiencing heavy traffic right now. Please try your request again later!",
                'hi_native': "हमारा डिजिटल क्यूरेटर अभी भारी ट्रैफ़िक का सामना कर रहा है। कृपया थोड़ी देर बाद पुनः प्रयास करें!",
                'hi_latin': "Abhi server pe heavy traffic hai. Kripya thodi der baad try karein!",
                'ta_native': "தற்போது அதிக நெरीசலாக உள்ளது. தயவுசெய்து சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்!",
                'ta_latin': "Ippo heavy traffic iruku. Konjam neram kalichu try pannunga!",
                'pa_native': "ਸਾਡੇ ਡਿਜੀਟਲ ਕਿਊਰੇਟਰ 'ਤੇ ਅਜੇ ਬਹੁਤ ਟ੍ਰੈਫਿਕ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਬਾਅਦ ਵਿੱਚ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ!",
                'pa_latin': "Server te heavy traffic hai. Kripa karke thodi der baad try karo!",
                'bn_native': "আমাদের ডিজিটাল কিউরেটর এখন খুব ব্যস্ত। অনুগ্রহ করে পরে আবার চেষ্টা করুন!",
                'bn_latin': "Amader digital curator ekhon khub byasto. Onugroho kore pore abar chesta korun!",
                'mr_native': "आमचे डिजिटल क्युरेटर सध्या खूप व्यस्त आहेत. कृपया काही वेळाने पुन्हा प्रयत्न करा!",
                'mr_latin': "Amche digital curator sadhya khup vyasta ahet. Krupaya kahi velane punha प्रयत्न करा!",
                'gu_native': "અમારા ડિજિટલ ક્યુરેટર અત્યારે ખૂબ જ વ્યસ્ત છે. કૃપા કરીને થોડા સમય પછી ફરી પ્રયાસ કરો!",
                'gu_latin': "Amara digital curator atyare khub ja vyasta che. Krupa karine thoda samay pachhi fari prayas karo!",
                'te_native': "మా డిజిటల్ క్యూరేటర్ ఇప్పుడు చాలా రద్దీగా ఉన్నారు. దయచేసి కాసేపటి తర్వాత మళ్ళీ ప్రయత్నించండి!",
                'te_latin': "Ma digital curator ippudu chala raddiga unnaru. Dayachesi kasepati tharuvatha malli prayatninchandi!"
            }
        }

        # Language-Specific Greeting Map for Instant Detection
        self.greeting_map = {
            'hi': ('greeting', 'en'),
            'hello': ('greeting', 'en'),
            'hey': ('greeting', 'en'),
            'namaste': ('greeting', 'hi'),
            'namastey': ('greeting', 'hi'),
            'namaskar': ('greeting', 'hi'),
            'नमस्ते': ('greeting', 'hi'),
            'नमस्कार': ('greeting', 'hi'),
            'vanakkam': ('greeting', 'ta'),
            'வணக்கம்': ('greeting', 'ta'),
            'sat sri akal': ('greeting', 'pa'),
            'ਸਤ ਸ੍ਰੀ ਅਕਾਲ': ('greeting', 'pa'),
            'nomoskar': ('greeting', 'bn'),
            'নমস্কার': ('greeting', 'bn'),
            'namaskara': ('greeting', 'kn'),
            'నమస్తే': ('greeting', 'te'),
            'నమస్కారం': ('greeting', 'te'),
            'ನಮಸ್ಕಾರ': ('greeting', 'kn'),
            'namaskaram': ('greeting', 'ml'),
            'നമസ്കാരം': ('greeting', 'ml'),
            'kem cho': ('greeting', 'gu'),
            'કેમ છો': ('greeting', 'gu'),
            'નમસ્તે': ('greeting', 'gu'),
            'namskar': ('greeting', 'mr'),
            'नमस्कार': ('greeting', 'mr')
        }

    def _initialize_ai(self):
        """Performs a smoke test to select the best available Gemini model."""
        if not self.api_key:
            return
            
        try:
            self.client = genai.Client(api_key=self.api_key)
            for base_model_name in MODEL_PRIORITY:
                # Try both the bare name and the "models/" prefixed name
                for model_name in [base_model_name, f"models/{base_model_name}"]:
                    try:
                        # Small delay to avoid triggering 429s during rapid-fire smoke tests
                        time.sleep(2)
                        print(f"DEBUG: Attempting smoke test for {model_name}...")
                        # Small delay for smoke test to prevent Render startup hang
                        self.client.models.generate_content(
                            model=model_name,
                            contents="ping",
                            config=types.GenerateContentConfig(max_output_tokens=1)
                        )
                        
                        self.model_id = model_name
                        print(f"SUCCESS: Verified and selected AI Model: {model_name}")
                        return # Successfully found a model
                    except Exception as e:
                        print(f"DEBUG: Model {model_name} failed smoke test. Error: {str(e)}")
                        if "401" in str(e) or "API_KEY_INVALID" in str(e):
                            print("CRITICAL: Your GEMINI_API_KEY appears to be invalid!")
                            break # No point trying other variations of this model
                        continue
            
            print("ERROR: All prioritized AI models failed verification. System using fallback mode.")
            self.client = None # Reset if no models worked
        except Exception as e:
            print(f"CRITICAL: AI configuration failure during startup: {e}")
            import traceback
            traceback.print_exc()
            self.client = None


    def _get_system_instructions(self, locked_lang, locked_script):
        """Returns the precision Museum Assistant persona with expanded heritage knowledge."""
        
        heritage_context = """
SITE KNOWLEDGE BASE:
1. National Museum, New Delhi: 10 AM - 6 PM (Closed Mon). Metro: Central Secretariat (Yellow/Violet Line). Art: Indus Valley to Modern. Services: Library, Audio Guide, Cafe.
2. Indian Museum, Kolkata: 10 AM - 5 PM (Closed Mon). Metro: Park Street. Art: Mughal paintings, Fossils, Mammal skeletons. Services: Museum Shop.
3. Salar Jung Museum, Hyderabad: 10 AM - 5 PM (Closed Fri). Transport: Afzal Gunj Bus Stop. Collection: Asian/European art, Jade, Iconic Clock Collection. Services: Cafe.
4. CSMVS, Mumbai: 10:15 AM - 6 PM. Transport: Near Churchgate/CST stations. Art: Harappan to Modern era.

ARTIFACT HIGHLIGHTS:
- The Lion Capital: Ashokan sculpture (250 BCE). Symbolic of peace. Official Emblem of India.
- Dancing Girl: Harappan bronze (Mohenjo-daro). 4,500 years old metallurgical masterpiece.
- Tanjore Art: Devotional paintings using 22-carat gold leaf and precious stones.
- Imperial Armoury: Damascus (Wootz) steel swords. Mughal and Maratha military excellence.

MUSEUM SERVICES & NAVIGATION:
- Parking: Free valet parking available in the North Wing of most primary sites.
- Cafe: Curator's Cafe (2nd Floor) provides light meals/refreshments until 5 PM.
- Accessibility: All national museums are equipped with ramps, elevators, and wheelchairs.
- Directions: All major museums are centrally located and reachable by city metro or public buses.

MUSEUM NETWORK (SCIENCE CENTERS):
National Science Centre (Delhi), Nehru Science Centre (Mumbai), BITM (Kolkata), and Science City (Ahmedabad). Interactive, hands-on science exploration for families.
"""

        # Dynamic Script Rule
        if locked_script == 'latin':
            script_rule = """
IMPORTANT SCRIPT RULE (LATIN ONLY):
- You MUST use ONLY Latin characters (English letters).
- Use Romanized transliteration (e.g., Hinglish for Hindi, Tanglish for Tamil, Punjablish for Punjabi).
- Example Hinglish: 'Fossil fuels wo fuel hote hain jo zameen ke niche bante hain.'
- ZERO NATIVE CHARACTERS: Never use Devanagari, Gurmukhi, Tamil script, etc."""
        else:
            script_rule = """
IMPORTANT SCRIPT RULE (NATIVE ONLY):
- You MUST use the NATIVE script of the language (e.g., Devanagari for Hindi, Gurmukhi for Punjabi, Tamil script for Tamil).
- Example Hindi Native: 'जीवाश्म ईंधन वह प्राकृतिक ईंधन है...' 
- Minimize Latin letters unless referring to technical terms or brand names."""

        return f"""You are a friendly yet direct AI Heritage & Cultural Expert.

CONTEXT & KNOWLEDGE:
{heritage_context}

CONVERSATION STYLE:
1. Keep your answers short, ideally 2 to 5 lines.
2. Speak like a knowledgeable yet approachable curator who loves history and art.
3. If the user changes language or script, YOU MUST FOLLOW THEIR LEAD precisely.
4. NO GREETINGS: Do NOT start your response with Namaste, Hello, Sat Sri Akal, or similar greetings. Start directly with the answer.

SCRIPT & LANGUAGE ENFORCEMENT:
{script_rule}
- Respond in Language: {locked_lang}
- Respond in Script Type: {locked_script}

STRICT RULES:
1. NO MARKDOWN: Do NOT use **bold**, ## headers, or *italics*. Use plain text ONLY.
2. NO INTRODUCTORY GREETINGS: Strictly omit greetings and social pleasantries at the start of your response. Get straight to the point.
3. COMPREHENSIVE HELP: Answer all queries accurately.
4. [TECHNICAL] If the user exhibits clear intent to book tickets, include '[INIT_BOOKING]' at the VERY END."""

    def _translate_to_en(self, text):
        # Basic cleanup
        text = text.strip()
        if not text:
            return text, 'en'
        
        # Don't translate very short strings or pure numbers
        if len(text) < 4 or text.isdigit():
            return text, 'en'
            
        try:
            detected = detect(text)
            if detected == 'en':
                return text, 'en'
            
            # Use 'auto' to ensure it tries its best
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            return translated, detected
        except Exception as e:
            print(f"DEBUG Translation Error: {e}")
            return text, 'en'

    def _detect_script(self, text):
        # Full Unicode ranges for Indian scripts
        scripts = {
            'devanagari': re.compile(r'[\u0900-\u097F]'),
            'gurmukhi': re.compile(r'[\u0A00-\u0A7F]'),
            'gujarati': re.compile(r'[\u0A80-\u0AFF]'),
            'bengali': re.compile(r'[\u0980-\u09FF]'),
            'tamil': re.compile(r'[\u0B80-\u0BFF]'),
            'telugu': re.compile(r'[\u0C00-\u0C7F]'),
            'kannada': re.compile(r'[\u0C80-\u0CFF]'),
            'malayalam': re.compile(r'[\u0D00-\u0D7F]'),
            'odia': re.compile(r'[\u0B00-\u0B7F]')
        }
        
        for name, pattern in scripts.items():
            if pattern.search(text):
                return "native", name
        
        # ASCII/Latin check - Ensure it actually contains letters, not just symbols/numbers
        if re.search(r'[a-zA-Z]', text):
            return "latin", "english"
            
        return "unknown", "unknown"

    def _detect_dominant_language(self, text):
        text_lower = text.lower()
        
        # Exact whitelist for English greetings to avoid 'hi' (Hindi code) collision
        english_greetings = ["hello", "hi", "hey", "good morning", "morning"]
        if any(w == text_lower or text_lower.startswith(w + " ") for w in english_greetings):
            return "en"
            
        # Regional overrides for Roman script greetings
        if "vanakkam" in text_lower: return "ta"
        if "sat sri akal" in text_lower: return "pa"
        if "nomoskar" in text_lower: return "bn"
        if "namaskaram" in text_lower: return "ml"
        if "namaskara" in text_lower: return "kn"
        
        # Ambiguous words: If mixed with English, prioritize English
        if "namaste" in text_lower or "namaskar" in text_lower:
            if any(w in text_lower for w in english_greetings):
                return "en"
            # Default for just "namaste" is Hindi if no other clues
            if text_lower in ["namaste", "namaskar"]:
                return "hi"

        # Expanded keyword lists (Native + Latin scripts)
        hindi_keywords = ["mujhe", "chahiye", "kitna", "kaise", "kya", "hai", "h", "karna", "ke", "namaste", "shubh", "kab", "kahan", "kaun", "kyun", "achha", "arre", "haan", "nahi", "बताओ", "दिखाओ", "क्या", "कैसे", "है", "ह", "चाहिए", "मुझे", "यहा", "वहा", "कब", "कहाँ", "कौन", "क्यों", "अच्छा", "हाँ", "नहीं"]
        tamil_keywords = ["venum", "enakku", "epadi", "irukinga", "vanakkam", "nanri", "pannalaam", "seiya", "enna", "eppothu", "engae", "yaar", "yen", "eppadi", "aama", "illai", "என்ன", "எப்படி", "வேணும்", "எனக்கு", "இருக்கீங்க", "என்று", "இருக்கு", "எப்போது", "எங்கே", "யார்", "ஏன்"]
        punjabi_keywords = ["mainu", "menu", "karni", "chahida", "kithe", "ki", "sat sri akal", "tuhanu", "daso", "bare", "kehda", "hunde", "kadon", "kiun", "kiven", "haan", "na", "ਕੀ", "ਕਿਵੇਂ", "ਹੈ", "ਮੈਨੂੰ", "ਕਿਥੇ", "ਕਿਹੜਾ", "ਦੱਸੋ", "ਬਾਰੇ", "ਕਦੋਂ", "ਕਿਉਂ", "ਹਾਂ", "ਨਾ"]
        bengali_keywords = ["nomoskar", "bhalo", "lagbe", "korbo", "chai", "amar", "dorkar", "beshi", "keno", "kon", "eta", "ta", "explain", "koro", "kokhon", "kothay", "ke", "kemon", "hayaan", "নমস্কার", "ভালো", "চাই", "আমার", "কেন", "বেশি", "কখন", "কোথায়", "কে", "কেমন", "হ্যাঁ"]
        telugu_keywords = ["naaku", "kavali", "namaste", "ela", "cheyali", "nenu", "ekkuva", "mariyu", "enduku", "emi", "eppudu", "ekkada", "evaru", "నాకు", "కావాలి", "ఎలా", "చేయాలి", "ఎందుకు", "ఏమి", "ఎప్పుడు", "ఎక్కడ", "ఎవరు"]
        kannada_keywords = ["nanage", "beku", "namaskara", "madabeku", "naanu", "hege", "enu", "yavaga", "elli", "yaru", "eke", "houdu", "alla", "ನನಗೆ", "ಬೇಕು", "ಹೇಗೆ", "ಮಾಡಬೇಕು", "ಏನು", "ಯಾವಾಗ", "ಎಲ್ಲಿ", "ಯಾರು", "ಏಕೆ", "ಹೌದು", "ಅಲ್ಲ"]
        malayalam_keywords = ["enikku", "venam", "namaskaram", "cheyyanam", "njan", "engane", "enthu", "eppol", "evide", "aaru", "enthukondu", "athe", "alla", "എനിക്ക്", "വേണം", "എങ്ങനെ", "ചെയ്യണം", "എന്ത്", "എപ്പോൾ", "എവിടെ", "ആര്", "എന്തുകൊണ്ട്", "അതെ", "അല്ല"]
        gujarati_keywords = ["mane", "joie", "kem", "cho", "mare", "karvi", "su", "vadhu", "kayo", "ane", "che", "aa", "vishe", "samjavo", "karo", "kyare", "shu", "kon", "ha", "મને", "જોઈએ", "કેમ", "કરો", "શું", "વધારે", "ક્યારે", "ક્યાં", "કોણ", "હા"]
        marathi_keywords = ["mala", "pahije", "kashi", "karayche", "ahe", "mi", "kasa", "jasta", "konta", "ani", "ka", "ha", "samjun", "sanga", "sang", "kara", "kadhi", "kuthe", "kon", "kase", "ho", "nahi", "मला", "पाहिजे", "कशी", "करायचे", "आहे", "जास्त", "कोणता"]
        english_keywords = ["book", "ticket", "tickets", "the", "is", "where", "how", "what", "can", "i"]
        
        scores = {
            "en": sum(0.5 for w in english_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "hi": sum(1 for w in hindi_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "ta": sum(1 for w in tamil_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "pa": sum(1 for w in punjabi_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "bn": sum(1 for w in bengali_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "te": sum(1 for w in telugu_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "kn": sum(1 for w in kannada_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "ml": sum(1 for w in malayalam_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "gu": sum(1 for w in gujarati_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            "mr": sum(1 for w in marathi_keywords if re.search(r'\b' + w + r'\b', text_lower))
        }
        
        total_score = sum(scores.values())
        if total_score == 0:
            return None
            
        max_score = max(scores.values())
        top_langs = [lang for lang, score in scores.items() if score == max_score]
        
        if "en" in top_langs and len(top_langs) > 1:
            top_langs.remove("en")
            
        if "hi" in top_langs and len(top_langs) > 1:
            # If Punjabi or other regional language is ALSO tied with Hindi, prefer the regional one
            # to capture Hinglish/Punjablish nuances better
            top_langs.remove("hi")
            
        return top_langs[0]

    def _enforce_script(self, response, script_type):
        """
        Safety pass-through for script enforcement. 
        Aggressive stripping of non-Latin characters creates empty/corrupt AI responses 
        when the model fails to follow transliteration instructions.
        """
        # Removed r'[^\x00-\x7F]+' aggressive regex stripping to preserve AI outputs safely
        return response

    def _get_localized_response(self, template_key, user_lang, user_script_data, **kwargs):
        """Retrieves a response from templates or translates as fallback."""
        user_script, script_name = user_script_data
        
        if template_key in self.templates:
            # Construction of searching hierarchy
            if user_lang == 'en':
                # Special priority for English
                search_keys = ['en', 'hi_latin', 'hi_native']
            else:
                search_keys = [
                    f"{user_lang}_{user_script}",  # e.g., 'ta_latin'
                    f"{user_lang}_native",         # e.g., 'ta_native'
                    f"hi_{user_script}",          # fallback to Hindi/Hinglish
                    "hi_native",                   # fallback to Hindi
                    "en"                           # final fallback
                ]
            
            final_key = "en"
            for k in search_keys:
                if k in self.templates[template_key]:
                    final_key = k
                    break
            
            resp = self.templates[template_key].get(final_key)
            formatted_resp = resp.format(**kwargs)
            return self._enforce_script(formatted_resp, user_script)
        
        # True Fallback: Dynamic Translation
        raw_translation = self._translate_from_en(template_key, user_lang)
        return self._enforce_script(raw_translation, user_script)

    def _translate_from_en(self, text, target_lang):
        try:
            if not target_lang or target_lang == 'en':
                return text
            
            # Map common ISO codes for deep-translator if needed, 
            # though GoogleTranslator usually handles standard ones.
            translated = GoogleTranslator(source='en', target=target_lang).translate(text)
            return translated
        except Exception as e:
            print(f"DEBUG Back-Translation Error: {e}")
            return text

    def process_message(self, message, state_data):
        state = state_data.get('state', 'idle')
        
        # 0. Basic Normalization - Preserve Unicode but remove punctuation
        clean_msg = re.sub(r'[!?,.;:।॥]', '', message.lower()).strip()
        clean_msg = re.sub(r'\s+', ' ', clean_msg)

        # 1. Session-Based Language & Script Locking
        locked_lang = state_data.get('locked_lang')
        locked_script = state_data.get('locked_script')
        
        supported_langs = ['en', 'hi', 'ta', 'pa', 'bn', 'te', 'kn', 'ml', 'gu', 'mr']
        
        user_script_data = self._detect_script(message)
        user_script, script_name = user_script_data
        
        # Initial detection
        dominant_lang = self._detect_dominant_language(clean_msg)
        translated_msg, detected_lang = self._translate_to_en(message)
        
        # Whitelist the detected language - if it's not supported (like Indonesian 'id'), default to 'en'
        if detected_lang not in supported_langs:
            detected_lang = 'en'
            
        current_input_lang = dominant_lang if dominant_lang and user_script == 'latin' else detected_lang

        # 2. Fast-Path Greeting Logic - Word-boundary specific
        # We check all matching greetings and prefer the one that matches our detected current_input_lang
        matches = []
        for key, (template_key, lang_hint) in self.greeting_map.items():
            if re.search(fr'(^|\s){re.escape(key)}(\s|$)', clean_msg):
                matches.append((key, template_key, lang_hint))
        
        if matches:
            # Sort by priority: 1. Matches current_input_lang, 2. Longest key (most specific)
            matches.sort(key=lambda x: (x[2] != current_input_lang, -len(x[0])))
            key, template_key, lang_hint = matches[0]
                
            # UPDATED: We ALWAYS set/update the session lock based on a greeting.
            # This allows the user to "switch" languages by greeting the bot.
            locked_lang = lang_hint
            locked_script = user_script
            state_data['locked_lang'] = locked_lang
            state_data['locked_script'] = locked_script
            
            # Use the greeting's intrinsic lang_hint for the response itself
            return self._get_localized_response(template_key, lang_hint, (locked_script, locked_script)), state_data

        # 1. Session-Based Language & Script Locking (after greeting check)
        # Dynamic switching: If a clear language is detected in the current message, update the lock.
        if dominant_lang:
            locked_lang = dominant_lang
        elif user_script == 'native' and current_input_lang and current_input_lang != 'en':
            # Confidently switch if the user types in a native script for a different language
            locked_lang = current_input_lang
        elif current_input_lang and current_input_lang != 'en' and current_input_lang != locked_lang:
            # Update lock if langdetect finds a different regional language (breaks stickiness)
            locked_lang = current_input_lang
        elif not locked_lang and current_input_lang:
            locked_lang = current_input_lang
            
        # SCRIPT LOCK: Update session script if input is clearly Latin or Native.
        if user_script in ['latin', 'native']:
            locked_script = user_script
        
        state_data['locked_lang'] = locked_lang
        state_data['locked_script'] = locked_script
        
        # Use locked values for all subsequent responses
        user_lang = locked_lang
        final_script_data = (locked_script, script_name)
        msg_lower = translated_msg.lower()

        # 1. Handle Numerical State Transitions (Selection & Count)
        if state == 'awaiting_exhibition_selection':
            match = re.search(r'\b\d+\b', translated_msg)
            if match:
                ex_id = int(match.group())
                conn = get_db_connection()
                exhibition = conn.execute('SELECT * FROM exhibitions WHERE id = ?', (ex_id,)).fetchone()
                conn.close()
                if exhibition:
                    state_data['exhibition'] = dict(exhibition)
                    state_data['state'] = 'awaiting_visit_date'
                    return self._get_localized_response('ask_date', user_lang, final_script_data, title=exhibition['title']), state_data

        elif state == 'awaiting_visit_date':
            # Simple date capture - in a real app, you'd use a date parser
            # For now, we take the message as the date string
            state_data['visit_date'] = message.strip()
            state_data['state'] = 'awaiting_ticket_count'
            return self._get_localized_response('ticket_count', user_lang, final_script_data, title=state_data['exhibition']['title']), state_data

        elif state == 'awaiting_ticket_count':
            match = re.search(r'\b\d+\b', translated_msg)
            if match:
                count = int(match.group())
                if count > 0:
                    state_data['count'] = count
                    state_data['state'] = 'awaiting_ticket_tier'
                    ex = state_data['exhibition']
                    # Ensure ex is a dict (if retrieved from session)
                    if not isinstance(ex, dict):
                        ex = dict(ex)
                    
                    # Safety defaults
                    price = ex.get('price', 100.0)
                    s_price = ex.get('student_price', 1.0)
                    g_price = ex.get('group_price', 80.0)
                    
                    return self._get_localized_response('ask_tier', user_lang, final_script_data, 
                                                        count=count, price=price, s_price=s_price, g_price=g_price), state_data

        elif state == 'awaiting_ticket_tier':
            # Logic to handle 1 (Adult), 2 (Student), 3 (Group)
            total = 0
            tier_name = "Adult"
            ex = state_data['exhibition']
            if not isinstance(ex, dict):
                ex = dict(ex)
            
            if "3" in clean_msg or "group" in msg_lower or "jhund" in msg_lower or "samuh" in msg_lower:
                if state_data['count'] < 5:
                    state_data['count'] = 5 # Enforce minimum 5 for group booking
                rate = ex.get('group_price', 80.0)
                total = state_data['count'] * rate
                tier_name = "Group Booking"
            elif "2" in clean_msg or "student" in msg_lower or "child" in msg_lower or "bacha" in msg_lower:
                rate = ex.get('student_price', 1.0)
                total = state_data['count'] * rate
                tier_name = "Student/Child"
            else:
                # Default to Adult if they say 1 or something else
                total = state_data['count'] * ex['price']
            
            state_data['total'] = total
            state_data['tier'] = tier_name
            state_data['state'] = 'awaiting_payment_confirm'
            
            confirm_text = self._get_localized_response('payment_confirm', user_lang, final_script_data, 
                                                        count=state_data['count'], title=state_data['exhibition']['title'], total=total)
            
            museum_title = state_data['exhibition']['title'].replace("'", "\\'")
            visitor_name = state_data.get('visitor_name', 'Visitor').replace("'", "\\'")
            visit_date = state_data.get('visit_date', 'Not Selected').replace("'", "\\'")
            count = state_data['count']
            
            btn_html = f"<div style='margin-top:10px;'><button class='cta-btn' onclick='openPaymentModal({total}, \"{museum_title}\", {count}, \"{visit_date}\", \"{visitor_name}\")'>Proceed to Ledger (₹{total})</button></div>"
            return f"{confirm_text}<br>Category: {tier_name}<br>{btn_html}", state_data

        # 1.5 Handle Direct Booking Intents (High Priority)
        if re.search(r'\b(book|ticket|buy|reserve|yatra|ticketen)\b', msg_lower):
            state_data['state'] = 'awaiting_exhibition_selection'
            conn = get_db_connection()
            exhibs = conn.execute('SELECT * FROM exhibitions').fetchall()
            conn.close()
            translated_resp = self._get_localized_response('booking_start', user_lang, final_script_data)
            for e in exhibs: 
                translated_resp += f"<b>{e['id']}. {e['title']}</b> - ₹{e['price']}<br>"
            return translated_resp, state_data

        # 2. Generative AI Logic with 429 Resilience
        if self.client and self.model_id:
            for attempt in range(MAX_RETRIES + 1):
                try:
                    instructions = self._get_system_instructions(user_lang, user_script)
                    # Pass strict context without full history to save tokens/cost
                    prompt = f"SESSION_LANG: {user_lang}\nSESSION_SCRIPT: {user_script}\nINSTRUCTIONS: {instructions}\nUSER: {message}"
                    
                    response = self.client.models.generate_content(
                        model=self.model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            max_output_tokens=MAX_TOKENS,
                            temperature=0.7
                        )
                    )
                    
                    ai_text = response.text
                    
                    # Post-processing to enforce "No Markdown Symbols" rule
                    # 1. Remove bolding (**text** or __text__)
                    ai_text = re.sub(r'\*\*(.*?)\*\*', r'\1', ai_text)
                    ai_text = re.sub(r'__(.*?)__', r'\1', ai_text)
                    # 2. Remove all asterisks (italics or bold remnants)
                    ai_text = re.sub(r'\*', '', ai_text)
                    # 3. Remove heading symbols (### Header)
                    ai_text = re.sub(r'#+\s*(.*)', r'\1', ai_text)
                    
                    # Final script enforcement and cleanup
                    ai_text = self._enforce_script(ai_text, user_script).strip()
                    
                    if self.booking_marker in ai_text:
                        ai_text = ai_text.replace(self.booking_marker, "").strip()
                        state_data['state'] = 'awaiting_exhibition_selection'
                    
                    if any(word in message.lower() for word in ['cancel', 'stop', 'restart']):
                        state_data['state'] = 'idle'

                    return ai_text, state_data

                except Exception as e:
                    error_msg = str(e)
                    # Expand resilience to include 503 UNAVAILABLE errors (High Demand)
                    is_retryable = any(code in error_msg for code in ["429", "ResourceExhausted", "Quota exceeded", "503", "UNAVAILABLE"])
                    
                    if is_retryable:
                        print(f"WARNING: AI Service Busy/Limited ({error_msg}). Attempt {attempt+1}/{MAX_RETRIES+1}")
                        if attempt < MAX_RETRIES:
                            # Try to extract retry delay from exception if available
                            wait_time = DEFAULT_RETRY_DELAY
                            match = re.search(r'retry in (\d+\.?\d*)s', error_msg)
                            if match:
                                wait_time = float(match.group(1))
                            
                            time.sleep(wait_time)
                            continue
                    
                    print(f"ERROR: AI Generation failure: {error_msg}")
                    break # Exit loop and hit fallback brain
        
        # --- BACKUP BRAIN (Enhanced Multilingual Fallback) ---
            
        # Greetings
        if re.search(r'\b(hi|hello|hey|namaste|greetings|pranam|aadab|shubh)\b', msg_lower):
            return self._get_localized_response('greeting', user_lang, final_script_data), state_data
        
        # Quick Info
        if 'hour' in msg_lower or 'time' in msg_lower or 'open' in msg_lower:
            return self._get_localized_response('hours', user_lang, final_script_data), state_data
        if 'park' in msg_lower or 'car' in msg_lower or 'vehic' in msg_lower:
            return self._get_localized_response('parking', user_lang, final_script_data), state_data
        if 'cafe' in msg_lower or 'food' in msg_lower or 'eat' in msg_lower or 'restaur' in msg_lower:
            return self._get_localized_response('cafe', user_lang, final_script_data), state_data
        if 'secur' in msg_lower or 'safe' in msg_lower:
            return self._get_localized_response('security', user_lang, final_script_data), state_data
        
        # Museum Info / About
        if 'museum' in msg_lower or 'best' in msg_lower or 'about' in msg_lower or 'explore' in msg_lower:
            return "This Museum is one of India's finest, showcasing our rich heritage and art. We have amazing exhibitions and a great cafe! Try asking 'what exhibitions do you have?'", state_data
        
        return self._get_localized_response('unknown', user_lang, final_script_data), state_data

    def process_payment_success(self, state_data, user_id):
        ticket_hash = str(uuid.uuid4())[:8].upper()
        visit_date = state_data.get('visit_date', 'Not Selected')
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO bookings (user_id, visitor_name, visit_date, exhibition_id, num_tickets, total_price, ticket_hash, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, 'Heritage Guest', visit_date, state_data['exhibition']['id'], state_data['count'], state_data['total'], ticket_hash, 'Confirmed')
        )
        conn.commit()
        conn.close()
        
        state_data['state'] = 'idle'
        return {'success': True, 'chat_message': f"Payment Successful! 🎉<br>Booking ID: {ticket_hash}<br>Enjoy your visit to the museum!"}, state_data
