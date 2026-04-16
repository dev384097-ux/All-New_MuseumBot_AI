import re

file_path = r'd:\CAPSTONE\chatbot_engine.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I want to replace everything from "self.templates = {" to the closing "}" of the unknown template.
# But first I need to find the correct start and end points.

start_pattern = r'self\.templates\s*=\s*\{'
# We'll look for the 'parking' or 'hours' templates as anchors since they might be past the corruption.
end_pattern = r"'\s*\}\s*\}\s*def\s+_initialize_ai" # Looking for the end of the class method

# Actually, I'll just find the first occurrence of greeting and the last occurrence of security/unknown.
# Or better, I will overwrite the entire _init_templates method.

new_method = """    def _init_templates(self):
        \"\"\"Initializes the static conversational phrases and maps.\"\"\"
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
                'en': "When do you plan to visit {title}?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>Select Date</button></div>",
                'hi_native': "आप {title} कब जाना चाहते हैं?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>तारीख चुनें</button></div>",
                'hi_latin': "Aap {title} kab visit karna chahte hain?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>Select Date</button></div>",
                'ta_native': "நீங்கள் எப்போது {title} செல்ல திட்டமிட்டுள்ளீர்கள்?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>தேதியைத் தேர்ந்தெடுக்கவும்</button></div>",
                'ta_latin': "Neenga eppo {title} visit panna plan panreenga?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>Select Date</button></div>",
                'pa_native': "ਤੁਸੀਂ {title} ਕਦੋਂ ਜਾਣ ਦੀ ਯੋਜਨਾ ਬਣਾ ਰਹੇ ਹੋ?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>ਤਾਰੀਖ ਚੁਣੋ</button></div>",
                'pa_latin': "Tusi {title} kadon visit karna chaunde ho?<br><div class='chat-picker-container'><input type='date' id='dc_{ts}' class='chat-date-input'><button onclick='submitChatDate(\"dc_{ts}\")' class='chat-date-btn'>Select Date</button></div>"
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
            'unknown': {
                'en': "I'm not sure about that. Try asking about 'exhibitions', 'hours', or 'tickets'!",
                'hi_native': "क्षमा करें, मुझे समझ नहीं आया। क्या आप 'टिकट' या 'समय' के बारे में पूछ सकते हैं?",
                'hi_latin': "Thoda clear karenge? Aap mujhse 'tickets' ya 'timings' ke bare mein puch sakte hain.",
                'ta_native': "என்னிடம் டிக்கெட்டுகள் அல்லது நேரங்களைப் பற்றி கேளுங்கள்!",
                'ta_latin': "Puriyala. Tickets illa hours pathi kelunga.",
                'pa_native': "ਮੈਨੂੰ ਸਮਝ ਨਹੀਂ ਆਈ। ਟਿਕਟਾਂ ਜਾਂ ਸਮੇਂ ਬਾਰੇ ਪੁੱਛੋ!",
                'pa_latin': "Samajh nai aayi. Tickets ya timings baare pucho."
            }
        }
"""

# Pattern to find the entire _init_templates method
# We search from "def _init_templates" up to the next method "def _initialize_ai"
method_pattern = r'def\s+_init_templates\(self\):.*?def\s+_initialize_ai\(self\)'

new_content = re.sub(method_pattern, new_method + '\n    def _initialize_ai(self)', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully fixed chatbot_engine.py")
