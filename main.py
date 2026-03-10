import os
import requests
import random
import json
import re

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DATASET_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"

SENT_FILE = "sent_hadiths.json"

THEMES = {
    "دعاء": ["دع"],
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

    sent.add(number)
    save_sent(sent)

    message = f"""
📜 <b>حديث اليوم</b>

{text}

📚 صحيح البخاري
Hadith #{number}

🏷️ الموضوع : {theme}
"""

    send_to_telegram(message)

    print("Hadith envoyé sans duplication.")


if __name__ == "__main__":
    main()
