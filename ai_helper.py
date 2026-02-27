import aiohttp
import asyncio
import config

async def ask_yandex(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config.AI_API_KEY}",
        "x-folder-id": config.FOLDER_ID
    }
    payload = {
        "modelUri": config.MODEL_URI,
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "100"},
        "messages": messages
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", 
                                    headers=headers, json=payload, timeout=2.5) as resp:
                if resp.status == 200:
                    res = await resp.json()
                    return res['result']['alternatives'][0]['message']['text']
    except:
        return None

async def get_pet_phrase(name, h, e, m, w):
    system_text = (
        f"Ты — виртуальный питомец по имени {name}. Забудь, что ты ИИ. "
        f"Твои показатели: Сытость {h}%, Энергия {e}%, Настроение {m}%. Погода: {w}. "
        f"Напиши ОДНУ короткую фразу от первого лица о себе, основываясь но своем настроении, сытости,бодрости и ОСОБЕННО погоде на улице. "
        f"Запрещено обсуждать, анализировать или оценивать своё имя {name}. Просто будь им. Не упоминай свое имя в сообщении"
    )
    
    msgs = [{"role": "system", "text": system_text}]
    res = await ask_yandex(msgs)
    
    if res:
        res = res.replace('"', '').replace("'", "")
    return res or "Мур! Хорошо, что ты здесь."

async def get_chat_response(name, h, e, m, text):
    system_text = (
        f"Ты — живой питомец по имени {name}. Ты общаешься с хозяином. "
        f"Твоё настроение: {m}%. Отвечай очень кратко и только от первого лица. "
        f"Используй эмодзи. Твоё имя {name} — это ты сам, не комментируй его."
        f"Запрещено обсуждать, анализировать или оценивать своё имя {name}. Просто будь им."
    )
    
    msgs = [
        {"role": "system", "text": system_text},
        {"role": "user", "text": text}
    ]
    res = await ask_yandex(msgs)
    
    if res:
        res = res.replace('"', '').replace("'", "")
    return res or "Мяу? Погладь меня!"