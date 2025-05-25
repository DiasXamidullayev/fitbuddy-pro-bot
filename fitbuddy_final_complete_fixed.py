from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import json
import os

LANG_FILE = "fitbuddy_lang.json"
PREMIUM_FILE = "fitbuddy_premium.json"

if os.path.exists(LANG_FILE):
    with open(LANG_FILE, "r") as f:
        user_lang = json.load(f)
else:
    user_lang = {}

if os.path.exists(PREMIUM_FILE):
    with open(PREMIUM_FILE, "r") as f:
        premium_users = json.load(f)
else:
    premium_users = {}

def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

lang_buttons = ReplyKeyboardMarkup(
    [[KeyboardButton("English"), KeyboardButton("Русский")]], resize_keyboard=True
)

menus = {
    "en": ReplyKeyboardMarkup(
        [[
            KeyboardButton("🔥 Calories"), KeyboardButton("📆 Plan"),
        ], [
            KeyboardButton("📈 Weight"), KeyboardButton("🍲 Recipes")
        ], [
            KeyboardButton("✅ Habits"), KeyboardButton("⏰ Reminders")
        ], [
            KeyboardButton("💎 Premium")
        ]],
        resize_keyboard=True,
    ),
    "ru": ReplyKeyboardMarkup(
        [[
            KeyboardButton("🔥 Калории"), KeyboardButton("📆 План"),
        ], [
            KeyboardButton("📈 Вес"), KeyboardButton("🍲 Рецепты")
        ], [
            KeyboardButton("✅ Привычки"), KeyboardButton("⏰ Напоминания")
        ], [
            KeyboardButton("💎 Премиум")
        ]],
        resize_keyboard=True,
    ),
}

texts = {
    "en": {
        "start": "Welcome! Choose your language:",
        "menu": "Main Menu",
        "already_premium": "✅ You already have Premium.",
        "premium_ad": (
            "💎 Premium Features Include:\n"
            "• Smart reminders\n"
            "• Export history\n"
            "• Personal plans\n"
            "• No ads\n\n"
            "👉 To get Premium, pay via ZoodPay or Payme and send /confirm @username"
        ),
        "confirm_hint": "Please provide a username, e.g. /confirm @john",
        "confirmed": "✅ Premium activated for {user}!",
        "notify": "✅ You have been granted Premium access. Thank you!",
    },
    "ru": {
        "start": "Добро пожаловать! Выберите язык:",
        "menu": "Главное меню",
        "already_premium": "✅ У вас уже есть Премиум.",
        "premium_ad": (
            "💎 В Премиум входят:\n"
            "• Умные напоминания\n"
            "• Экспорт данных\n"
            "• Персональные планы\n"
            "• Без рекламы\n\n"
            "👉 Чтобы получить Премиум, оплатите через ZoodPay или Payme и напишите /confirm @username"
        ),
        "confirm_hint": "Укажите имя пользователя, например /confirm @user",
        "confirmed": "✅ Премиум активирован для {user}!",
        "notify": "✅ Вам активирован Premium-доступ. Спасибо за оплату!",
    }
}

LANGUAGE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts["en"]["start"], reply_markup=lang_buttons)
    return LANGUAGE

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = "en" if update.message.text == "English" else "ru"
    user_lang[user_id] = lang
    save(LANG_FILE, user_lang)
    await update.message.reply_text(texts[lang]["menu"], reply_markup=menus[lang])
    return ConversationHandler.END

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    if user_id in premium_users:
        await update.message.reply_text(texts[lang]["already_premium"])
    else:
        await update.message.reply_text(texts[lang]["premium_ad"], parse_mode="Markdown")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(texts["en"]["confirm_hint"])
        return
    target_username = context.args[0]
    target_id = context.user_data.get("id", "")
    if target_username:
        premium_users[target_username] = True
        save(PREMIUM_FILE, premium_users)
        await update.message.reply_text(texts["en"]["confirmed"].format(user=target_username))
        try:
            await context.bot.send_message(chat_id=target_id, text=texts["en"]["notify"])
        except:
            pass

def main():
    app = ApplicationBuilder().token("PASTE_YOUR_BOT_TOKEN").build()

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_lang)]},
        fallbacks=[]
    ))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(MessageHandler(filters.Regex("^(💎 Premium|💎 Премиум)$"), premium))

    app.run_polling()

if __name__ == "__main__":
    main()