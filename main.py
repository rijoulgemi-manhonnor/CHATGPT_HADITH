import os
import requests
import random

# =========================
# Configuration
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DATASET_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.json"

# thèmes et mots-clés associés
THEMES = {
    "دعاء": ["دعاء", "يدعو", "ادع"],
    "صبر": ["صبر", "يصبر", "صابر"],
    "صلاة": ["صلاة", "يصلي", "صلوا"],
    "رمضان": ["رمضان", "صوم", "صيام"],
    "صدقة": ["صدقة", "تصدق", "مال"]
}

# =========================
# Charger les hadiths
# =========================

def fetch_hadiths():
    r = requests.get(DATASET_URL)
    r.raise_for_status()
    data = r.json()
    return data["hadiths"]


# =========================
# Filtrer par thème
# =========================

def filter_by_theme(hadiths, keywords):

    results = []

    for h in hadiths:
        text = h["text"]

        for k in keywords:
            if k in text:
                results.append(h)
                break

    return results


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

    requests.post(url, json=payload).raise_for_status()


# =========================
# Programme principal
# =========================

def main():

    hadiths = fetch_hadiths()

    # choisir thème aléatoire
    theme = random.choice(list(THEMES.keys()))

    keywords = THEMES[theme]

    filtered = filter_by_theme(hadiths, keywords)

    if not filtered:
        print("Aucun hadith trouvé pour ce thème")
        return

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

    print(f"Hadith envoyé (thème: {theme})")


if __name__ == "__main__":
    main()
