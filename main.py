import os
import requests
import random
import json
import re

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DATASET_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"

SENT_FILE = "sent_hadiths.json"

THEMES = {
    "دعاء": ["دع"],
    "صبر": ["صبر"],
    "صلاة": ["صل"],
    "صيام": ["صوم"],
    "صدقة": ["صدق"]
}


def normalize_arabic(text):

    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)

    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")

    return text


def fetch_hadiths():

    r = requests.get(DATASET_URL)
    r.raise_for_status()
    return r.json()["hadiths"]


def load_sent():

    if not os.path.exists(SENT_FILE):
        return set()

    with open(SENT_FILE) as f:
        return set(json.load(f))


def save_sent(sent):

    with open(SENT_FILE, "w") as f:
        json.dump(list(sent), f)


def filter_by_theme(hadiths, keywords):

    results = []

    for h in hadiths:

        text = normalize_arabic(h["text"])

        for k in keywords:
            if k in text:
                results.append(h)
                break

    return results


# =========================
# Explication IA avec Groq
# =========================

def generate_explanation(hadith_text):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
اشرح هذا الحديث النبوي شرحا بسيطا ومختصرا في سطرين فقط:

{hadith_text}
"""

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    r = requests.post(url, headers=headers, json=payload)

    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"].strip()


def send_to_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload).raise_for_status()


def main():

    hadiths = fetch_hadiths()

    sent = load_sent()

    theme = random.choice(list(THEMES.keys()))

    keywords = THEMES[theme]

    filtered = filter_by_theme(hadiths, keywords)

    available = [h for h in filtered if h["hadithnumber"] not in sent]

    if not available:
        available = hadiths

    hadith = random.choice(available)

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

    print("Hadith + explication envoyé.")


if __name__ == "__main__":
    main()
