import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = "8247328023:AAHRG3_cUlfDAeIdebZG7b6vDTtkmJCjxkc"
WEATHER_API_KEY = "008e618ba99dfb1f10325cb6600f951c"
AI_API_KEY = "AQVN3cMiHvzoYE1oFMqWqEJi3zJnqEpBfTO9QkFt" 
FOLDER_ID = "b1gqmkt2t9r690953rdu"
MODEL_URI = f"gpt://{FOLDER_ID}/yandexgpt-lite/latest@tamr8u7d2tusnivlc9cmf"
DB_NAME = os.path.join(BASE_DIR, "pets_database.db")
IMAGE_PATHS = {
    "boy": {
        "happy": os.path.join(BASE_DIR, "images", "boy_happy.png"),
        "sad": os.path.join(BASE_DIR, "images", "boy_sad.png"),
        "hungry": os.path.join(BASE_DIR, "images", "boy_hungry.png"),
        "sleepy": os.path.join(BASE_DIR, "images", "boy_sleepy.png"),
        "normal": os.path.join(BASE_DIR, "images", "boy_normal.png"),
        "sick": os.path.join(BASE_DIR, "images", "boy_sick.png"),
        "gone": os.path.join(BASE_DIR, "images", "boy_gone.png"),
        "playing": os.path.join(BASE_DIR, "images", "boy_playing.png")
    },
    "girl": {
        "happy": os.path.join(BASE_DIR, "images", "girl_happy.png"),
        "sad": os.path.join(BASE_DIR, "images", "girl_sad.png"),
        "hungry": os.path.join(BASE_DIR, "images", "girl_hungry.png"),
        "sleepy": os.path.join(BASE_DIR, "images", "girl_sleepy.png"),
        "normal": os.path.join(BASE_DIR, "images", "girl_normal.png"),
        "sick": os.path.join(BASE_DIR, "images", "girl_sick.png"),
        "gone": os.path.join(BASE_DIR, "images", "girl_gone.png"),
        "playing": os.path.join(BASE_DIR, "images", "girl_playing.png")
    }
}
ANAGRAMS = ["кошка", "клубок", "молоко", "мышка", "рыбка", "когтеточка", "сметана"]