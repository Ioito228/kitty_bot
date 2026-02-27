import asyncio, random, time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import config, database as db, weather, ai_helper
from pet import Pet

# Кэши
PHOTO_CACHE = {}
USER_CACHE = {}

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

class PetStates(StatesGroup):
    naming = State()
    choosing_gender = State()
    chatting = State()
    changing_city = State()
    playing_math = State()
    playing_anagram = State()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍎 Покормить", callback_data="act_feed"), 
         InlineKeyboardButton(text="💤 Сон", callback_data="act_sleep")],
        [InlineKeyboardButton(text="💊 Лечить", callback_data="act_heal"), 
         InlineKeyboardButton(text="💬 Общаться", callback_data="act_chat")],
        [InlineKeyboardButton(text="🎮 Игры", callback_data="menu_games"), 
         InlineKeyboardButton(text="📊 Статус", callback_data="act_status")],
        [InlineKeyboardButton(text="🏙 Сменить город", callback_data="act_city")]
    ])

async def send_optimized_photo(target, img_path, caption, reply_markup=None):
    if img_path in PHOTO_CACHE:
        return await target.answer_photo(PHOTO_CACHE[img_path], caption=caption, 
                                        reply_markup=reply_markup, parse_mode="Markdown")
    msg = await target.answer_photo(FSInputFile(img_path), caption=caption, 
                                    reply_markup=reply_markup, parse_mode="Markdown")
    PHOTO_CACHE[img_path] = msg.photo[-1].file_id
    return msg

async def update_cache_bg(uid, data):
    try:
        name, gender, h, e, m, city, hlth = data
        w_res = await weather.get_weather(city)
        w_txt = w_res[1]
        phrase = await ai_helper.get_pet_phrase(name, h, e, m, w_txt)
        USER_CACHE[uid] = {"phrase": phrase, "weather": w_txt, "time": time.time()}
    except:
        pass

async def show_pet_home(target, data):
    if isinstance(target, types.CallbackQuery):
        await target.answer()
        msg_target = target.message
        uid = target.from_user.id
    else:
        msg_target = target
        uid = target.from_user.id
    
    name, gender, h, e, m, city, hlth = data
    cached = USER_CACHE.get(uid, {"phrase": "Я так рад тебя видеть!", "weather": "Загрузка..."})
    
    p = Pet(name, gender, h, e, m, hlth)
    img_path = config.IMAGE_PATHS.get(gender, config.IMAGE_PATHS['boy']).get(p.get_emotion(), "normal")
    
    await send_optimized_photo(msg_target, img_path, 
                              f"{p.get_status_text(cached['weather'])}\n\n💬 {cached['phrase']}", 
                              main_kb())
    asyncio.create_task(update_cache_bg(uid, data))

# --- ИГРЫ ---
async def start_math_game(cb: types.CallbackQuery, state: FSMContext):
    a, b = random.randint(10, 60), random.randint(10, 60)
    await state.update_data(math_res=a + b)
    await cb.answer()
    await cb.message.answer(f"🧠 Реши пример: {a} + {b} = ?")
    await state.set_state(PetStates.playing_math)

async def start_anagram_game(cb: types.CallbackQuery, state: FSMContext):
    word = random.choice(config.ANAGRAMS)
    shuffled = "".join(random.sample(word, len(word)))
    await state.update_data(ana_ans=word)
    await cb.answer()
    await cb.message.answer(f"🔤 Собери слово из букв: **{shuffled}**", parse_mode="Markdown")
    await state.set_state(PetStates.playing_anagram)

async def process_game_result(user_id, correct, reward, state):
    data = await state.get_data()
    raw = await db.load_pet_data(user_id)
    if not raw:
        return "Ошибка загрузки питомца"
    
    p = Pet(*raw[:5], raw[6])
    if correct:
        p.mood = min(100, p.mood + reward)
        result = f"✅ Верно! Настроение +{reward}%"
    else:
        answer = data.get("math_res") or data.get("ana_ans")
        result = f"❌ Неверно. Правильный ответ: {answer}"
    
    await db.save_pet(user_id, p, raw[5])
    await state.clear()
    return result

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    data = await db.load_pet_data(m.from_user.id)
    if data:
        await show_pet_home(m, data)
    else:
        await m.answer("Привет! Как назовём твоего питомца?")
        await state.set_state(PetStates.naming)

@dp.callback_query(F.data == "act_status")
async def btn_status(cb: types.CallbackQuery):
    data = await db.load_pet_data(cb.from_user.id)
    if data:
        await show_pet_home(cb, data)

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
async def math_callback(cb: types.CallbackQuery, state: FSMContext):
    await start_math_game(cb, state)

@dp.callback_query(F.data == "play_anagram")
async def anagram_callback(cb: types.CallbackQuery, state: FSMContext):
    await start_anagram_game(cb, state)

@dp.message(PetStates.playing_math)
async def math_answer(m: types.Message, state: FSMContext):
    data = await state.get_data()
    result = await process_game_result(m.from_user.id, 
                                       m.text == str(data.get("math_res")), 
                                       15, state)
    await m.answer(result, reply_markup=main_kb())

@dp.message(PetStates.playing_anagram)
async def anagram_answer(m: types.Message, state: FSMContext):
    data = await state.get_data()
    result = await process_game_result(m.from_user.id,
                                       m.text.lower().strip() == data.get("ana_ans", "").lower(),
                                       20, state)
    await m.answer(result, reply_markup=main_kb())

@dp.callback_query(F.data == "act_chat")
async def btn_chat(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("О чем хочешь поговорить? (Напиши 'Стоп' для выхода)")
    await state.set_state(PetStates.chatting)

@dp.message(PetStates.chatting)
async def chat_proc(m: types.Message, state: FSMContext):
    if m.text.lower() in ["стоп", "выход", "назад"]:
        await state.clear()
        await m.answer("Закончили разговор.", reply_markup=main_kb())
        return
    
    raw = await db.load_pet_data(m.from_user.id)
    if not raw:
        await m.answer("Ошибка загрузки питомца")
        return
    
    await bot.send_chat_action(m.chat.id, "typing")
    res = await ai_helper.get_chat_response(raw[0], raw[2], raw[3], raw[4], m.text)
    await m.answer(res)

@dp.callback_query(F.data.startswith("act_"))
async def acts_handler(cb: types.CallbackQuery):
    if cb.data in ["act_status", "act_chat", "act_city"]:
        return
    
    raw = await db.load_pet_data(cb.from_user.id)
    if not raw:
        await cb.answer("Ошибка загрузки питомца", show_alert=True)
        return
    
    p = Pet(*raw[:5], raw[6])
    
    actions = {
        "act_feed": ("🍎 Покормить", p.feed),
        "act_sleep": ("💤 Сон", p.sleep),
        "act_heal": ("💊 Лечить", p.heal)
    }
    
    if cb.data in actions:
        msg = actions[cb.data][1]()
        await db.save_pet(cb.from_user.id, p, raw[5])
        await cb.answer(msg, show_alert=True)
        await show_pet_home(cb, await db.load_pet_data(cb.from_user.id))

@dp.callback_query(F.data == "act_city")
async def city_btn(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Введи название города:")
    await state.set_state(PetStates.changing_city)

@dp.message(PetStates.changing_city)
async def city_logic(m: types.Message, state: FSMContext):
    raw = await db.load_pet_data(m.from_user.id)
    if not raw:
        await m.answer("Ошибка загрузки питомца")
        return
    
    p = Pet(*raw[:5], raw[6])
    await db.save_pet(m.from_user.id, p, m.text)
    await state.clear()
    await m.answer(f"Теперь мы живем в городе {m.text}!", reply_markup=main_kb())

@dp.message(PetStates.naming)
async def naming_proc(m: types.Message, state: FSMContext):
    await state.update_data(n=m.text)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👦 Мальчик", callback_data="sex_boy"),
        InlineKeyboardButton(text="👧 Девочка", callback_data="sex_girl")
    ]])
    await m.answer(f"Какого пола будет {m.text}?", reply_markup=kb)
    await state.set_state(PetStates.choosing_gender)

@dp.callback_query(PetStates.choosing_gender)
async def sex_proc(cb: types.CallbackQuery, state: FSMContext):
    gender = "boy" if "boy" in cb.data else "girl"
    sd = await state.get_data()
    p = Pet(sd['n'], gender)
    await db.save_pet(cb.from_user.id, p, "Москва")
    await state.clear()
    await cb.message.answer(f"Твой питомец {sd['n']} готов!", reply_markup=main_kb())

async def time_loop():
    while True:
        await asyncio.sleep(600)
        uids = await db.get_all_user_ids()
        for uid in uids:
            try:
                raw = await db.load_pet_data(uid)
                if not raw:
                    continue
                p = Pet(*raw[:5], raw[6])
                imp, _ = await weather.get_weather(raw[5])
                p.time_passes(imp)
                if p.health <= 0:
                    await db.delete_pet(uid)
                else:
                    await db.save_pet(uid, p, raw[5])
            except:
                pass

async def main():
    await db.init_db()
    asyncio.create_task(time_loop())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())