CyberSathi (سائبر سیٹھی)

CyberSathi is a bilingual (English and Urdu) cybersecurity assistant built for everyday users in Pakistan. It helps people identify online scams, understand digital threats (like OTP fraud or deepfakes), and provides direct links to the NCCIA to report cybercrimes.

The Problem
Many people in Pakistan fall victim to cyber scams because the advice available is too technical, only in English, and hard to find.

Our Solution
CyberSathi runs 100% locally on the user's computer using open-weight AI (Ollama). This means no personal data is ever sent to the cloud, ensuring complete privacy. 

Features:
Scam Checker: Users can type their problem in English or Roman Urdu, and the AI replies in simple English or proper Urdu script.
- Risk Badges: Instantly shows if a message is High, Medium, or Low risk.
- Voice Input: Uses OpenAI Whisper locally to transcribe English voice to text.
- Reporting: Direct links to the National Cyber Crime Investigation Agency (NCCIA).

 How to Run Locally
1. Install Ollama from ollama.com.
2. Download the model by running: `ollama pull llama3.2:1b`
3. Install FFmpeg (required for voice): `winget install Gyan.FFmpeg`
4. Open the folder in your terminal and create a virtual environment: `python -m venv .venv`
5. Activate it: `.\.venv\Scripts\activate`
6. Install dependencies: `pip install -r requirements.txt`
7. Run the app: `streamlit run app.py`

Tech Stack
- Streamlit (Python)
- Ollama (llama3.2:1b)
- OpenAI Whisper