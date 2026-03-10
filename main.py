import os
import requests
import random
import re

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DATASET_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"

THEMES = {
    "دعاء": ["دع", "يدع", "دعاء"],
    "صبر": ["صبر"],
    "صلاة": ["صل", "صلاة"],
    "صيام": ["صوم", "صيام"],
    "صدقة": ["صدق", "صدقة", "تصدق"]
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

    theme = random.choice(list(THEMES.keys()))

    keywords = THEMES[theme]

    filtered = filter_by_theme(hadiths, keywords)

    if not filtered:
        hadith = random.choice(hadiths)
        theme = "عام"
    else:
        hadith = random.choice(filtered)

    text = hadith["text"]
    number = hadith["hadithnumber"]

    message = f"""
📜 <b>حديث اليوم</b>

{text}

📚 صحيح البخاري
Hadith #{number}

🏷️ الموضوع : {theme}
"""

    send_to_telegram(message)

    print("Hadith envoyé avec succès.")


if __name__ == "__main__":
    main()
