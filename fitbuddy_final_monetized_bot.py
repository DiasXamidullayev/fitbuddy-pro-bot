
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
import json, os

LANGUAGE, CAL_W, CAL_H, CAL_A, CAL_G, CAL_Goal = range(6)
user_names = {}

LANG_FILE = "user_lang.json"
PREMIUM_FILE = "premium_users.json"

def load(file): return json.load(open(file)) if os.path.exists(file) else {}
def save(file, data): json.dump(data, open(file, "w"), ensure_ascii=False, indent=2)

user_lang = load(LANG_FILE)
premium_users = load(PREMIUM_FILE)

texts = {
    "en": {
        "start": "👋 Welcome to FitBuddy! Choose your language:"
    },
    "ru": {
        "start": "👋 Добро пожаловать в FitBuddy! Выберите язык:"
    }
}

lang_buttons = ReplyKeyboardMarkup(
    [[KeyboardButton("English"), KeyboardButton("Русский")]], resize_keyboard=True
)

menus = {
    "en": ReplyKeyboardMarkup(
        [["🔥 Calories", "📆 Plan"], ["📈 Weight", "🍲 Recipes"], ["✅ Habits", "⏰ Reminders"], ["💎 Premium"]],
        resize_keyboard=True
    ),
    "ru": ReplyKeyboardMarkup(
        [["🔥 Калории", "📆 План"], ["📈 Вес", "🍲 Рецепты"], ["✅ Привычки", "⏰ Напоминание"], ["💎 Премиум"]],
        resize_keyboard=True
    )
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts["en"]["start"], reply_markup=lang_buttons)
    return LANGUAGE

if __name__ == "__main__":
    app = ApplicationBuilder().token("PASTE_YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    print("✅ FitBuddy bot is running...")
    app.run_polling()
