class Pet:
    def __init__(self, name, gender, hunger=100, energy=100, mood=100, health=100):
        self.name = name
        self.gender = gender
        self.hunger = hunger
        self.energy = energy
        self.mood = mood
        self.health = health
    def get_emotion(self):
        if self.health <= 0: return "gone"
        if self.health < 35: return "sick"
        if self.hunger < 35: return "hungry"
        if self.energy < 35: return "sleepy"
        if self.mood < 40: return "sad"
        if self.hunger > 85 and self.energy > 85 and self.mood > 85: return "happy"
        return "normal"
    def get_status_text(self, weather_txt):
        return (f"🐾 *{self.name}*\n━━━━━━━━━━━━━━━\n"
                f"❤️ Здоровье: {self.health}%\n🍎 Сытость: {self.hunger}%\n"
                f"⚡ Энергия: {self.energy}%\n😊 Настроение: {self.mood}%\n🏙 Погода: {weather_txt}")
    def feed(self):
        if self.hunger >= 100: return "Я уже сыт! 🍎"
        self.hunger = min(100, self.hunger + 25)
        self.mood = min(100, self.mood + 5)
        return "Мням! Очень вкусно 🍎"
    def sleep(self):
        if self.energy >= 100: return "Я не хочу спать! 💤"
        self.energy = min(100, self.energy + 50)
        return "Хр-р-р... Сплю... 💤"
    def heal(self):
        if self.health >= 100: return "Я здоров! 💊"
        self.health = min(100, self.health + 40)
        return "Лекарство помогло! 💊"
    def time_passes(self, w_impact=0):
        self.hunger = max(0, self.hunger - 5)
        self.energy = max(0, self.energy - 5)
        self.mood = max(0, self.mood - 5 + w_impact)
        if self.hunger <= 10 or self.energy <= 10:
            self.health = max(0, self.health - 10)