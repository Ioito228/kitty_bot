class Pet:
    def __init__(self, name, gender, hunger=100, energy=100, mood=100, health=100):
        self.name = name
        self.gender = gender
        self.hunger = hunger
        self.energy = energy
        self.mood = mood
        self.health = health

    def get_emotion(self):
        if self.health < 30:
            return "sick"
        if self.hunger < 40 or self.mood < 40:
            return "sad"
        return "happy"

    def get_status_text(self, weather_txt):
        return (
            f"🐾 *{self.name}*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"❤️ Здоровье: {self.health}%\n"
            f"🍎 Сытость: {self.hunger}%\n"
            f"⚡ Энергия: {self.energy}%\n"
            f"😊 Настроение: {self.mood}%\n"
            f"🏙 Погода: {weather_txt}"
        )

    def feed(self):
        if self.hunger >= 100:
            return "Я не хочу кушать!"
        self.hunger = min(100, self.hunger + 25)
        return "Очень вкусно! 🍎"

    def sleep(self):
        if self.energy >= 100:
            return "Я не хочу спать!"
        self.energy = min(100, self.energy + 40)
        self.mood = min(100, self.mood + 10)
        return "Сладких снов... 💤"

    def heal(self):
        if self.health >= 100:
            return "Я здоров!"
        self.health = min(100, self.health + 30)
        return "Теперь мне лучше! 💊"

    def time_passes(self, weather_impact=0):
        self.hunger = max(0, self.hunger - 7)
        self.energy = max(0, self.energy - 5)
        self.mood = max(0, self.mood - 6 + weather_impact)
        
        if self.hunger < 20 or self.energy < 20:
            self.health = max(0, self.health - 10)