import os, re

def clean_key(key: str) -> str:
    return re.sub(r'[^\x21-\x7E]', '', key).strip()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOT_TOKEN = "8558737655:AAHKeVZNQfAzd7Yx0q06a3Pdtb8bn8hCa_Q"
WEATHER_API_KEY = "008e618ba99dfb1f10325cb6600f951c"
AI_API_KEY = "AQVN3cMiHvzoYE1oFMqWqEJi3zJnqEpBfTO9QkFt" 
FOLDER_ID = "b1gqmkt2t9r690953rdu"
MODEL_URI = "gpt://b1gqmkt2t9r690953rdu/yandexgpt-lite/latest@tamr8u7d2tusnivlc9cmf"
DB_NAME = os.path.join(BASE_DIR, "pets_database.db")
IMAGE_PATHS = {
    "boy": {k: os.path.join(BASE_DIR, "images", f"boy_{k}.png") for k in ["happy", "sad", "hungry", "sleepy", "normal", "sick"]},
    "girl": {k: os.path.join(BASE_DIR, "images", f"girl_{k}.png") for k in ["happy", "sad", "hungry", "sleepy", "normal", "sick"]}
}

IMAGE_PLAY = {
    "boy": os.path.join(BASE_DIR, "images", "boy_playing.png"),
    "girl": os.path.join(BASE_DIR, "images", "girl_playing.png")
}

IMAGE_GONE = {
    "boy": os.path.join(BASE_DIR, "images", "boy_gone.png"),
    "girl": os.path.join(BASE_DIR, "images", "girl_gone.png")
}

ANAGRAMS = ["кошка", "клубок", "молоко", "мышка", "рыбка", "когтеточка", "сметана"]