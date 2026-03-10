import os
import requests
import random

# =========================
# Configuration
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DATASET_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"


# =========================
# Charger les hadiths
# =========================

def fetch_hadiths():
    response = requests.get(DATASET_URL)
    response.raise_for_status()
    data = response.json()
    return data["hadiths"]


# =========================
# Choisir un hadith aléatoire
# =========================

def get_random_hadith(hadiths):
    return random.choice(hadiths)


# =========================
# Envoyer message Telegram
# =========================

def send_to_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()


# =========================
# Programme principal
# =========================

def main():

    hadiths = fetch_hadiths()

    hadith = get_random_hadith(hadiths)

    text = hadith["text"]
    number = hadith["hadithnumber"]

    message = f"""
📜 <b>حديث اليوم</b>

{text}

📚 صحيح البخاري
Hadith #{number}
"""

    send_to_telegram(message)

    print("Hadith envoyé avec succès.")


if __name__ == "__main__":
    main()
