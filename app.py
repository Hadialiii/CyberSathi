import streamlit as st
import ollama
import whisper
import tempfile
import os
from streamlit_mic_recorder import mic_recorder

# TELL PYTHON EXACTLY WHERE FFMPEG IS
os.environ["PATH"] += os.pathsep + r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"

st.set_page_config(page_title="CyberSathi", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400..700&display=swap');
    
    .stApp { background-color: #FFF0F5; }
    
    /* HEADINGS - Rockwell, Bold */
    h1, h2, h3, .report-box h3 { 
        font-family: 'Rockwell', 'Courier Bold', Courier, serif !important;
        font-weight: bold !important;
    }
    
    h1 { color: #D6336C !important; text-align: center; letter-spacing: 1px; }
    
    /* ALL OTHER TEXT - Times New Roman */
    html, body, [class*="css"], p, li, div.stMarkdown, .subtitle { 
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    .subtitle { color: #8B3A62; text-align: center; font-size: 18px; margin-bottom: 30px; }
    
    .stTextInput > div > div > input { 
        border: 2px solid #FFB6C1; border-radius: 10px; 
        background-color: #FFFAFA; 
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    .stButton > button {
        background-color: white !important; color: #D6336C !important;
        border: 2px solid #FFB6C1 !important; border-radius: 8px !important;
        font-family: 'Times New Roman', Times, serif !important; font-weight: bold !important;
    }
    
    .stMarkdown p, .stMarkdown li { font-size: 16px !important; line-height: 1.6 !important; color: #333333; }
    
    .report-box { 
        background-color: #FFE4E1; padding: 25px; border-radius: 15px; 
        border: 2px solid #FFB6C1; margin-top: 30px; 
        box-shadow: 2px 2px 10px rgba(214, 51, 108, 0.1);
    }
    .report-box h3 { color: #D6336C; margin-bottom: 15px; font-size: 22px; }
    .report-box p, .report-box li { color: #4A4A4A; font-size: 17px; line-height: 1.7; }
    
    .stLinkButton > a { 
        background-color: #D6336C !important; color: white !important; 
        border-radius: 10px; padding: 15px 24px; font-weight: bold; display: block; 
        margin-top: 15px; font-family: 'Times New Roman', Times, serif !important;
        font-size: 18px; text-align: center; text-decoration: none;
    }
    
    .urdu-text { 
        font-family: 'Noto Nastaliq Urdu', serif !important; 
        text-align: right; 
        font-size: 20px;
        line-height: 2.5;
    }

    /* Kiro's Risk Badges */
    .risk-high { background-color: #FF4444; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 18px; text-align: center; margin: 10px 0; }
    .risk-medium { background-color: #FF8C00; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 18px; text-align: center; margin: 10px 0; }
    .risk-low { background-color: #2E8B57; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 18px; text-align: center; margin: 10px 0; }

    /* Kiro's Chat History */
    .chat-user { background-color: #FFE4EF; border-radius: 12px; padding: 12px 16px; margin: 8px 0; text-align: right; border-left: 4px solid #D6336C; }
    .chat-bot { background-color: #FFFAFA; border-radius: 12px; padding: 12px 16px; margin: 8px 0; border-left: 4px solid #FFB6C1; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ CyberSathi")

language = st.radio("Choose Language / زبان منتخب کریں:", ("English", "اردو (Urdu)"), horizontal=True)

@st.cache_resource
def load_whisper():
    return whisper.load_model("small")

if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def update_text():
    st.session_state.user_input = st.session_state.text_box

# Kiro's Risk Detector
SCAM_KEYWORDS_HIGH = ["otp", "pin", "password", "bank account", "send money", "transfer", "prize", "lottery", "won", "click link", "verify", "your account is blocked", "blackmail", "nude", "video leak", "pay now", "urgent", "expire", "paisa bhejo", "account band", "link click", "inaam", "jeet"]
SCAM_KEYWORDS_MEDIUM = ["job offer", "work from home", "earn money", "investment", "crypto", "government officer", "officer", "police", "arrested", "case filed", "sim swap", "number port", "pta", "tax refund", "noc"]

def detect_risk(text: str) -> tuple[str, str]:
    low = text.lower()
    if any(k in low for k in SCAM_KEYWORDS_HIGH):
        return "high", "🔴 HIGH RISK — Likely Scam!"
    if any(k in low for k in SCAM_KEYWORDS_MEDIUM):
        return "medium", "🟠 MEDIUM RISK — Be Careful"
    return "low", "🟢 LOW RISK — Seems Safe"

def show_risk_badge(text: str, lang: str):
    level, label = detect_risk(text)
    if lang == "اردو (Urdu)":
        labels_ur = {"high": "🔴 خطرہ زیادہ — ممکنہ دھوکہ!", "medium": "🟠 درمیانہ خطرہ — محتاط رہیں", "low": "🟢 خطرہ کم — محفوظ لگتا ہے"}
        label = labels_ur[level]
    st.markdown(f"<div class='risk-{level}'>{label}</div>", unsafe_allow_html=True)

def render_chat_history():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>🛡️ {msg['content']}</div>", unsafe_allow_html=True)

def build_messages(system_prompt: str, new_query: str) -> list:
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": new_query})
    return messages

# ══════════════════════════════════════════════════════════════════════════════
# ENGLISH MODE
# ══════════════════════════════════════════════════════════════════════════════
if language == "English":
    st.markdown('<p class="subtitle">Confused about a message, call, or link? Ask below or use the mic.</p>', unsafe_allow_html=True)
    
    st.write("**Try a quick scenario:**")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    question_to_ask = ""
    if col1.button("📞 OTP Call"): question_to_ask = "Someone called saying they are from my bank and asked for my OTP."
    if col2.button("🎥 Deepfake Video"): question_to_ask = "My cousin video called me asking for money, but their face looked weird and they hung up quickly."
    if col3.button("🔗 Suspicious Link"): question_to_ask = "I got a WhatsApp message saying I won a prize and need to click a link to claim it."
    if col4.button("💼 Fake Job Offer"): question_to_ask = "I received a job offer on WhatsApp with a very high salary but they are asking for a registration fee."
    if col5.button("👮 Fake Officer"): question_to_ask = "Someone called claiming to be a police officer and said I have a case registered against me."
    if col6.button("📱 SIM Swap"): question_to_ask = "My mobile network suddenly stopped working and I can't make calls or use data."

    st.write("🎤 **Or click to Record:**")
    audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", just_once=True, use_container_width=True, key="recorder_en")

    if audio:
        if not audio.get("bytes") or len(audio["bytes"]) < 1000:
            st.warning("No audio detected. Please speak clearly and try again.")
        else:
            with st.spinner("Transcribing... Please wait."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio["bytes"])
                        tmp_path = tmp_file.name
                    model = load_whisper()
                    result = model.transcribe(tmp_path, language="en")
                    st.session_state.user_input = result["text"]
                    os.remove(tmp_path)
                    st.rerun()
                except Exception as e:
                    st.error(f"Transcription error: {e}")

    user_input = st.text_input("Type your confusion here:", value=st.session_state.user_input, key="text_box", on_change=update_text)
    final_query = question_to_ask if question_to_ask else user_input
    
    system_prompt = (
        "You are CyberSathi, a friendly cybersecurity assistant for everyday users in Pakistan. "
        "Your job is to help people understand if they are being scammed or not. "
        "Always answer in simple, clear English — no technical jargon. "
        "Structure your answer as: 1) Is this a scam? (yes/no/maybe), 2) Why?, 3) What should they do right now? "
        "Use short sentences. Be warm and reassuring, not alarming."
    )

# ══════════════════════════════════════════════════════════════════════════════
# URDU MODE (Text Only, No Mic)
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<p class="subtitle urdu-text">کسی میسج، کال یا لنک سے پریشان ہیں؟ نیچے لکھیں۔</p>', unsafe_allow_html=True)

    st.write("**فوری سوالات / Quick Scenarios:**")
    ucol1, ucol2, ucol3 = st.columns(3)
    question_to_ask = ""
    if ucol1.button("📞 OTP کال"): question_to_ask = "کسی نے بینک سے ہونے کا دعویٰ کرتے ہوئے میرا OTP مانگا۔"
    if ucol2.button("🔗 مشکوک لنک"): question_to_ask = "واٹس ایپ پر میسج آیا کہ میں نے انعام جیتا ہے، لنک پر کلک کریں۔"
    if ucol3.button("💼 جعلی نوکری"): question_to_ask = "مجھے واٹس ایپ پر بڑی تنخواہ والی نوکری کی آفر آئی لیکن رجسٹریشن فیس مانگ رہے ہیں۔"

    user_input = st.text_input("یہاں لکھیں (مثلاً: mera phone chori ho gaya hai)", value=st.session_state.user_input, key="text_box", on_change=update_text)
    final_query = question_to_ask if question_to_ask else user_input
    
    system_prompt = (
        "آپ سائبر ساتھی ہیں — پاکستانی عام لوگوں کے لیے ایک دوستانہ سائبر سیکیورٹی مددگار۔ "
        "صرف اردو میں جواب دیں۔ آسان الفاظ استعمال کریں، کوئی تکنیکی اصطلاح نہیں۔ "
        "جواب کا ڈھانچہ یہ رکھیں: 1) کیا یہ دھوکہ ہے؟ (ہاں/نہیں/شاید)، 2) کیوں؟، 3) ابھی کیا کریں؟ "
        "مختصر جملے لکھیں۔ پرسکون اور مددگار انداز رکھیں۔"
    )

# ══════════════════════════════════════════════════════════════════════════════
# RENDER CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.chat_history:
    st.markdown("---")
    st.write("**💬 Conversation / گفتگو:**" if language == "English" else "**💬 گفتگو:**")
    render_chat_history()

# ══════════════════════════════════════════════════════════════════════════════
# PROCESS QUERY
# ══════════════════════════════════════════════════════════════════════════════
if final_query:
    show_risk_badge(final_query, language)

    with st.spinner("Thinking..." if language == "English" else "سوچ رہا ہے..."):

        # --- HARDCODED: Stolen phone in Urdu ---
        if language == "اردو (Urdu)" and any(w in final_query.lower() for w in ["chori", "stolen", "gum", "khoya"]):
            hardcoded_urdu = (
                "اگر آپ کا فون چوری ہو گیا ہے تو فوراً یہ 3 کام کریں:\n\n"
                "1. اپنے نیٹ ورک پرووائیڈر (جاز، ٹیلی نار، وغیرہ) کو کال کر کے اپنی سم بلاک کروائیں۔\n"
                "2. اپنے فون کا IMEI نمبر پولیس کو رپورٹ کریں۔\n"
                "3. نیشنل سائبر کرائم ایجنسی (NCCIA) کی ویب سائٹ پر جا کر آن لائن شکایت درج کریں۔"
            )
            st.markdown("### 💡 جواب:")
            st.markdown(f"<div class='urdu-text'><b>{hardcoded_urdu}</b></div>", unsafe_allow_html=True)
            st.session_state.chat_history.append({"role": "user", "content": final_query})
            st.session_state.chat_history.append({"role": "assistant", "content": hardcoded_urdu})

        # --- NORMAL AI RESPONSE ---
        else:
            client = ollama.Client(host="http://127.0.0.1:11434")
            messages = build_messages(system_prompt, final_query)

            response = client.chat(model="llama3.2:1b", messages=messages, stream=True)

            st.markdown("### 💡 Answer:" if language == "English" else "### 💡 جواب:")
            answer_placeholder = st.empty()
            full_response = ""

            for chunk in response:
                full_response += chunk["message"]["content"]
                if language == "English":
                    answer_placeholder.markdown(f"**{full_response}▌**")
                else:
                    answer_placeholder.markdown(f"<div class='urdu-text'><b>{full_response}▌</b></div>", unsafe_allow_html=True)

            # Remove streaming cursor
            if language == "English":
                answer_placeholder.markdown(f"**{full_response}**")
            else:
                answer_placeholder.markdown(f"<div class='urdu-text'><b>{full_response}</b></div>", unsafe_allow_html=True)

            st.session_state.chat_history.append({"role": "user", "content": final_query})
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    st.session_state.user_input = ""

# Clear conversation button
if st.session_state.chat_history:
    if st.button("🗑️ Clear Conversation" if language == "English" else "🗑️ گفتگو صاف کریں"):
        st.session_state.chat_history = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# REPORT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
if language == "English":
    st.markdown("""
    <div class="report-box">
        <h3>🚨 Want to report this crime?</h3>
        <p>If someone is blackmailing you, making fake videos of you, or stealing your money, report it immediately to the <strong>National Cyber Crime Investigation Agency (NCCIA)</strong>.</p>
        <ul>
            <li><strong>Official Helpline:</strong> 1799</li>
            <li><strong>Email:</strong> helpdesk@nccia.gov.pk</li>
            <li><strong>Police Emergency:</strong> 15</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Go to NCCIA Website", "https://complaint.nccia.gov.pk/", use_container_width=True)
else:
    st.markdown("""
    <div class="report-box urdu-text" style="text-align: right;">
        <h3>🚨 کیا آپ اس جرم کی رپورٹ کرنا چاہتے ہیں؟</h3>
        <p>اگر کوئی آپ کو بلیک میل کر رہا ہے، آپ کی جعلی ویڈیوز بنا رہا ہے، یا آپ کے پیسے چرا رہا ہے، تو فوراً <strong>نیشنل سائبر کرائم انویسٹی گیشن ایجنسی (NCCIA)</strong> کو رپورٹ کریں۔</p>
        <ul style="list-style-type: none;">
            <li><strong>سرکاری ہیلپ لائن:</strong> 1799</li>
            <li><strong>ای میل:</strong> helpdesk@nccia.gov.pk</li>
            <li><strong>پولیس ایمرجنسی:</strong> 15</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("NCCIA ویب سائٹ پر جائیں", "https://complaint.nccia.gov.pk/", use_container_width=True)  