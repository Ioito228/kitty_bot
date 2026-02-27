import aiohttp
import time
import config

# Кэш: { "Москва": (время_обновления, impact, "текст_погоды") }
WEATHER_CACHE = {}

async def get_weather(city):
    now = time.time()
    
    # Если данные есть в кэше и они свежие (меньше 15 минут), берем их
    if city in WEATHER_CACHE:
        cache_time, impact, text = WEATHER_CACHE[city]
        if now - cache_time < 900: 
            return impact, text

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=3) as resp:
                if resp.status == 200:
                    d = await resp.json()
                    temp = d['main']['temp']
                    desc = d['weather'][0]['description'].capitalize()
                    impact = 2 if "ясно" in desc.lower() or "облачно" in desc.lower() else -3
                    result_text = f"{desc}, {temp}°C"
                    
                    # Сохраняем в кэш
                    WEATHER_CACHE[city] = (now, impact, result_text)
                    return impact, result_text
    except:
        pass
    return 0, "Нет данных"