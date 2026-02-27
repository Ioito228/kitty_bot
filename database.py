import aiosqlite
import config

async def init_db():
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            pet_name TEXT,
            gender TEXT,
            hunger INTEGER DEFAULT 80,
            energy INTEGER DEFAULT 80,
            mood INTEGER DEFAULT 80,
            city TEXT DEFAULT 'Москва',
            health INTEGER DEFAULT 100
        )''')
        await db.commit()

async def load_pet_data(user_id):
    async with aiosqlite.connect(config.DB_NAME) as db:
        async with db.execute(
            "SELECT pet_name, gender, hunger, energy, mood, city, health FROM users WHERE user_id = ?", 
            (user_id,)
        ) as cur:
            return await cur.fetchone()

async def save_pet(user_id, pet_obj, city):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO users 
            (user_id, pet_name, gender, hunger, energy, mood, city, health) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
            (user_id, pet_obj.name, pet_obj.gender, pet_obj.hunger, 
             pet_obj.energy, pet_obj.mood, city, pet_obj.health))
        await db.commit()

async def get_all_user_ids():
    async with aiosqlite.connect(config.DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]

async def delete_pet(user_id):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()