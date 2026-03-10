import os
import random
import json
import requests
from openai import OpenAI

# =========================
# CONFIG
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DATASET_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"

SENT_FILE = "sent_hadiths.json"

THEMES = [
    "دعاء",
    "صبر",
    "صلاة",
    "صيام",
    "صدقة",
    "توبة",
    "أخلاق"
]

# =========================
# GROQ CLIENT
# =========================

groq = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =========================
# LOAD HADITH DATA
# =========================

def fetch_hadiths():

    r = requests.get(DATASET_URL)
    r.raise_for_status()

    return r.json()["hadiths"]


# =========================
# SENT HADITH STORAGE
# =========================

def load_sent():

    if not os.path.exists(SENT_FILE):
        return set()

    with open(SENT_FILE) as f:
        return set(json.load(f))


def save_sent(sent):

    with open(SENT_FILE, "w") as f:
        json.dump(list(sent), f)


# =========================
# IA THEME DETECTION
# =========================

def detect_theme(hadith_text):

    prompt = f"""
حدد موضوع هذا الحديث من القائمة التالية فقط:

دعاء
صبر
صلاة
صيام
صدقة
توبة
أخلاق

أجب بكلمة واحدة فقط.

الحديث:
{hadith_text}
"""

    response = groq.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt,
        temperature=0
    )

    return response.output_text.strip()


# =========================
# IA EXPLANATION
# =========================

def generate_explanation(hadith_text):

    prompt = f"""
اشرح هذا الحديث النبوي شرحا بسيطا ومختصرا في سطرين:

{hadith_text}
"""

    response = groq.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt,
        temperature=0.3
    )

    return response.output_text.strip()


# =========================
# FIND HADITH BY THEME
# =========================

def find_hadith_by_theme(hadiths, theme, sent):

    random.shuffle(hadiths)

    for h in hadiths[:40]:

        if h["hadithnumber"] in sent:
            continue

        detected = detect_theme(h["text"])

        if theme in detected:
            return h

    return random.choice(hadiths)


# =========================
# TELEGRAM SEND
# =========================

def send_to_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    r = requests.post(url, json=payload)

    r.raise_for_status()


# =========================
# MAIN
# =========================

def main():

    hadiths = fetch_hadiths()

    sent = load_sent()

    theme = random.choice(THEMES)

    hadith = find_hadith_by_theme(hadiths, theme, sent)

    text = hadith["text"]
    number = hadith["hadithnumber"]

    explanation = generate_explanation(text)

    sent.add(number)
    save_sent(sent)

    message = f"""
📜 <b>حديث اليوم</b>

{text}

💡 <b>شرح مختصر</b>
{explanation}

📚 صحيح البخاري
Hadith #{number}

🏷️ الموضوع : {theme}
"""

    send_to_telegram(message)

    print("Hadith envoyé avec thème et explication.")


if __name__ == "__main__":
    main()
