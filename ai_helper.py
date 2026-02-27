import aiohttp
import config

async def ask_yandex(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config.AI_API_KEY}",
        "x-folder-id": config.FOLDER_ID
    }
    payload = {
        "modelUri": config.MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "100"
        },
        "messages": messages
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion", 
                headers=headers, 
                json=payload, 
                timeout=10
            ) as resp:
                res_json = await resp.json()
                if resp.status == 200:
                    return res_json['result']['alternatives'][0]['message']['text']
                else:
                    # ВЫВОД ОШИБКИ В КОНСОЛЬ
                    print(f"Ошибка ИИ (Код {resp.status}): {res_json}")
    except Exception as e:
        print(f"Ошибка подключения к ИИ: {e}")
    
    return None

async def get_pet_phrase(name, h, e, m, w):
    system_text = f"Ты виртуальный питомец {name}. Твои статы: здоровье {h}%, энергия {e}%, настроение {m}%. Погода: {w}. Напиши 1 короткую фразу от себя, зависящую от твоего настроения, сытости,энергии и ОСОБЕННО погоды, удели ей отдельное внимание."
    msgs = [{"role": "system", "text": system_text}]
    res = await ask_yandex(msgs)
    if res: return res.replace('"', '').strip()
    return "Я так рад тебя видеть!"

async def get_chat_response(name, h, e, m, text):
    system_text = f"Ты живой питомец по имени {name}. Твое настроение {m}%. Отвечай хозяину кратко с эмодзи."
    msgs = [{"role": "system", "text": system_text}, {"role": "user", "text": text}]
    res = await ask_yandex(msgs)
    if res: return res.replace('"', '').strip()
    return "Мяу? Я задумался, погладь меня!"