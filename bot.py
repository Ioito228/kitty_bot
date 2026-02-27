import asyncio, random, time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import config, database as db, weather, ai_helper
from pet import Pet

PHOTO_CACHE = {}
USER_CACHE = {}
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

class PetStates(StatesGroup):
    naming, choosing_gender, chatting, changing_city, playing_math, playing_anagram = State(), State(), State(), State(), State(), State()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍎 Покормить", callback_data="act_feed"), InlineKeyboardButton(text="💤 Сон", callback_data="act_sleep")],
        [InlineKeyboardButton(text="💊 Лечить", callback_data="act_heal"), InlineKeyboardButton(text="💬 Общаться", callback_data="act_chat")],
        [InlineKeyboardButton(text="🎮 Игры", callback_data="menu_games"), InlineKeyboardButton(text="📊 Статус", callback_data="act_status")],
        [InlineKeyboardButton(text="🏙 Сменить город", callback_data="act_city")]
    ])

async def send_optimized_photo(target, img_path, caption, reply_markup=None):
    if img_path in PHOTO_CACHE: 
        return await target.answer_photo(PHOTO_CACHE[img_path], caption=caption, reply_markup=reply_markup, parse_mode="Markdown")
    msg = await target.answer_photo(FSInputFile(img_path), caption=caption, reply_markup=reply_markup, parse_mode="Markdown")
    PHOTO_CACHE[img_path] = msg.photo[-1].file_id
    return msg

async def update_cache_bg(uid, data):
    try:
        name, gender, h, e, m, city, hlth = data
        w_res = await weather.get_weather(city)
        w_txt = w_res[1]
        phrase = await ai_helper.get_pet_phrase(name, h, e, m, w_txt)
        if phrase:
            USER_CACHE[uid] = {"phrase": phrase, "weather": w_txt, "time": time.time()}
    except: pass

async def show_pet_home(m_cb, data):
    if not data:
        target = m_cb if isinstance(m_cb, types.Message) else m_cb.message
        await target.answer("Питомец не найден. Напиши /start!")
        return
    if isinstance(m_cb, types.CallbackQuery): await m_cb.answer()
    uid = m_cb.from_user.id
    name, gender, h, e, m, city, hlth = data
    cached = USER_CACHE.get(uid, {"phrase": "Привет! Я скучал!", "weather": "Загрузка..."})
    p = Pet(name, gender, h, e, m, hlth)
    img_path = config.IMAGE_PATHS[gender][p.get_emotion()]
    target = m_cb if isinstance(m_cb, types.Message) else m_cb.message
    await send_optimized_photo(target, img_path, f"{p.get_status_text(cached['weather'])}\n\n💬 {cached['phrase']}", main_kb())
    asyncio.create_task(update_cache_bg(uid, data))

@dp.message(Command("start"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    data = await db.load_pet_data(m.from_user.id)
    if data: await show_pet_home(m, data)
    else:
        await m.answer("Привет! Давай заведем питомца. Как его назовем?")
        await state.set_state(PetStates.naming)

@dp.callback_query(F.data == "act_status")
async def btn_status(cb: types.CallbackQuery):
    data = await db.load_pet_data(cb.from_user.id)
    await show_pet_home(cb, data)

@dp.callback_query(F.data == "act_chat")
async def btn_chat(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Пиши питомцу! Напиши 'Стоп' для выхода.")
    await state.set_state(PetStates.chatting)

@dp.callback_query(F.data == "act_city")
async def btn_city(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Напиши название своего города. Это важно, потому что я чувствую погоду там, где ты находишься!")
    await state.set_state(PetStates.changing_city)

@dp.callback_query(F.data.startswith("act_"))
async def acts_handler(cb: types.CallbackQuery):
    if cb.data in ["act_status", "act_chat", "act_city"]: return
    raw = await db.load_pet_data(cb.from_user.id)
    if not raw: return
    p = Pet(*raw[:5], raw[6])
    if cb.data == "act_feed": msg = p.feed()
    elif cb.data == "act_sleep": msg = p.sleep()
    elif cb.data == "act_heal": msg = p.heal()
    else: return
    await db.save_pet(cb.from_user.id, p, raw[5])
    await cb.answer(msg, show_alert=True)
    await show_pet_home(cb, await db.load_pet_data(cb.from_user.id))

@dp.message(PetStates.chatting)
async def chat_proc(m: types.Message, state: FSMContext):
    if m.text and m.text.lower() in ["стоп", "выход"]:
        await state.clear()
        await m.answer("Закончили разговор.", reply_markup=main_kb())
        return
    raw = await db.load_pet_data(m.from_user.id)
    await bot.send_chat_action(m.chat.id, "typing")
    res = await ai_helper.get_chat_response(raw[0], raw[2], raw[3], raw[4], m.text)
    p = Pet(*raw[:5], raw[6])
    p.mood = min(100, p.mood + 5)
    await db.save_pet(m.from_user.id, p, raw[5])
    await m.answer(res)

@dp.message(PetStates.changing_city)
async def city_proc(m: types.Message, state: FSMContext):
    raw = await db.load_pet_data(m.from_user.id)
    if not raw: return
    p = Pet(*raw[:5], raw[6])
    await db.save_pet(m.from_user.id, p, m.text)
    await state.clear()
    await m.answer(f"Теперь наш город: {m.text}!", reply_markup=main_kb())

@dp.callback_query(F.data == "menu_games")
async def btn_games(cb: types.CallbackQuery):
    await cb.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Математика", callback_data="play_math")],
        [InlineKeyboardButton(text="🔤 Анаграммы", callback_data="play_anagram")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="act_status")]
    ])
    await cb.message.answer("Во что поиграем?", reply_markup=kb)

@dp.callback_query(F.data == "play_math")
async def math_start(cb: types.CallbackQuery, state: FSMContext):
    raw = await db.load_pet_data(cb.from_user.id)
    a, b = random.randint(10, 60), random.randint(10, 60)
    await state.update_data(m_res = a + b)
    await cb.answer()
    await send_optimized_photo(cb.message, config.IMAGE_PATHS[raw[1]]["playing"], f"🧠 {a} + {b} = ?")
    await state.set_state(PetStates.playing_math)

@dp.message(PetStates.playing_math)
async def math_logic(m: types.Message, state: FSMContext):
    sd = await state.get_data(); raw = await db.load_pet_data(m.from_user.id)
    p = Pet(*raw[:5], raw[6])
    if m.text == str(sd.get("m_res")):
        p.mood = min(100, p.mood + 15); txt = "✅ Верно!"
    else: txt = f"❌ Нет, ответ {sd.get('m_res')}"
    await db.save_pet(m.from_user.id, p, raw[5]); await state.clear(); await m.answer(txt, reply_markup=main_kb())

@dp.callback_query(F.data == "play_anagram")
async def ana_start(cb: types.CallbackQuery, state: FSMContext):
    raw = await db.load_pet_data(cb.from_user.id)
    word = random.choice(config.ANAGRAMS)
    sh = "".join(random.sample(word, len(word)))
    await state.update_data(ans=word); await cb.answer()
    await send_optimized_photo(cb.message, config.IMAGE_PATHS[raw[1]]["playing"], f"🔤 Сложи слово: {sh}")
    await state.set_state(PetStates.playing_anagram)

@dp.message(PetStates.playing_anagram)
async def ana_logic(m: types.Message, state: FSMContext):
    sd = await state.get_data(); raw = await db.load_pet_data(m.from_user.id)
    p = Pet(*raw[:5], raw[6])
    if m.text.lower().strip() == sd.get("ans"):
        p.mood = min(100, p.mood + 20); txt = "✅ Правильно!"
    else: txt = f"❌ Ошибка, это {sd.get('ans')}"
    await db.save_pet(m.from_user.id, p, raw[5]); await state.clear(); await m.answer(txt, reply_markup=main_kb())

@dp.message(PetStates.naming)
async def naming_proc(m: types.Message, state: FSMContext):
    await state.update_data(n=m.text); await state.set_state(PetStates.choosing_gender)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👦 Мальчик", callback_data="sex_boy"),
        InlineKeyboardButton(text="👧 Девочка", callback_data="sex_girl")
    ]])
    await m.answer(f"Пол для {m.text}?", reply_markup=kb)

@dp.callback_query(PetStates.choosing_gender)
async def sex_proc(cb: types.CallbackQuery, state: FSMContext):
    g = "boy" if "boy" in cb.data else "girl"
    sd = await state.get_data(); p = Pet(sd['n'], g)
    await db.save_pet(cb.from_user.id, p, "Москва"); await state.clear()
    await cb.message.answer(f"Питомец готов!", reply_markup=main_kb())

async def time_loop():
    while True:
        await asyncio.sleep(600)
        uids = await db.get_all_user_ids()
        for uid in uids:
            try:
                raw = await db.load_pet_data(uid)
                if not raw: continue
                p = Pet(*raw[:5], raw[6])
                imp, _ = await weather.get_weather(raw[5])
                p.time_passes(imp)
                if p.health <= 0: await db.delete_pet(uid)
                else: await db.save_pet(uid, p, raw[5])
            except: pass

async def main():
    await db.init_db()
    asyncio.create_task(time_loop())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())