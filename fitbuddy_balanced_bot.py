from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
import json
import os

LANGUAGE, CAL_W, CAL_H, CAL_A, CAL_G, CAL_Goal = range(6)

LANG_FILE = "user_lang.json"
PREMIUM_FILE = "premium_users.json"

def load(file): return json.load(open(file)) if os.path.exists(file) else {}
def save(file, data): json.dump(data, open(file, "w"), ensure_ascii=False, indent=2)

user_lang = load(LANG_FILE)
premium_users = load(PREMIUM_FILE)

lang_buttons = ReplyKeyboardMarkup([[KeyboardButton("English 🇬🇧"), KeyboardButton("Русский 🇷🇺")]], resize_keyboard=True)

menus = {
    "en": ReplyKeyboardMarkup(
        [["🔥 Calories", "📆 Plan"], ["📈 Progress", "🍽️ Recipes"], ["✅ Checklist", "⏰ Reminder"], ["💎 Premium"]],
        resize_keyboard=True),
    "ru": ReplyKeyboardMarkup(
        [["🔥 Калории", "📆 План"], ["📈 Вес", "🍽️ Рецепты"], ["✅ Привычки", "⏰ Напоминание"], ["💎 Премиум"]],
        resize_keyboard=True)
}
texts = {
    "en": {
        "start": "👋 Welcome to FitBuddy! Choose your language:",
        "menu": "Choose an action:",
        "not_premium": "🚫 This feature is Premium only. Use /premium to upgrade.",
        "premium": "💳 Get Premium: https://your-payment-link.com",
        "already_premium": "💎 You already have Premium.",
        "cal_q1": "Enter your weight (kg):",
        "cal_q2": "Now your height (cm):",
        "cal_q3": "Your age:",
        "cal_q4": "Gender (m/f):",
        "cal_q5": "Goal? (gain / lose / maintain):",
        "cal_result": "✅ Your daily calorie need: {cal} kcal",
        "plan_text": "📆 Weekly Plan:\n- Mon: Cardio\n- Wed: Strength\n- Fri: Full body",
        "progress_saved": "✅ Your weight has been saved!",
        "recipe": "🍽️ Sample recipe: Oats + banana + peanut butter (350 kcal)",
        "checklist": "✅ What did you complete today? (water / workout)",
        "reminder_locked": "⏰ Smart reminders are Premium only."
    },
    "ru": {
        "start": "👋 Добро пожаловать в FitBuddy! Выберите язык:",
        "menu": "Выберите действие:",
        "not_premium": "🚫 Эта функция доступна только в Premium. Введите /premium для обновления.",
        "premium": "💳 Получите Premium: https://your-payment-link.com",
        "already_premium": "💎 У вас уже есть Premium.",
        "cal_q1": "Введите ваш вес (кг):",
        "cal_q2": "Теперь рост (см):",
        "cal_q3": "Возраст:",
        "cal_q4": "Пол (м/ж):",
        "cal_q5": "Цель? (масса / похудение / поддержание):",
        "cal_result": "✅ Ваша дневная норма: {cal} ккал",
        "plan_text": "📆 План на неделю:\n- Пн: Кардио\n- Ср: Силовая\n- Пт: Всё тело",
        "progress_saved": "✅ Вес записан!",
        "recipe": "🍽️ Пример: овсянка + банан + арахис (350 ккал)",
        "checklist": "✅ Что вы сделали сегодня? (вода / тренировка)",
        "reminder_locked": "⏰ Умные напоминания только для Premium."
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts["en"]["start"], reply_markup=lang_buttons)
    return LANGUAGE

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = "en" if "English" in update.message.text else "ru"
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
        await update.message.reply_text(texts[lang]["premium"])
        # === Calories (free)
async def calories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(str(update.effective_user.id), "en")
    await update.message.reply_text(texts[lang]["cal_q1"])
    return CAL_W

async def cal_w(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["w"] = float(update.message.text)
    lang = user_lang.get(str(update.effective_user.id), "en")
    await update.message.reply_text(texts[lang]["cal_q2"])
    return CAL_H

async def cal_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["h"] = float(update.message.text)
    lang = user_lang.get(str(update.effective_user.id), "en")
    await update.message.reply_text(texts[lang]["cal_q3"])
    return CAL_A

async def cal_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["a"] = int(update.message.text)
    lang = user_lang.get(str(update.effective_user.id), "en")
    await update.message.reply_text(texts[lang]["cal_q4"])
    return CAL_G

async def cal_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["g"] = update.message.text.lower()
    lang = user_lang.get(str(update.effective_user.id), "en")
    await update.message.reply_text(texts[lang]["cal_q5"])
    return CAL_Goal

async def cal_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    w = context.user_data["w"]
    h = context.user_data["h"]
    a = context.user_data["a"]
    g = context.user_data["g"]
    lang = user_lang.get(str(update.effective_user.id), "en")
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g.startswith("m") or g == "м" else -161)
    cal = bmr + 300 if "gain" in goal or "масса" in goal else bmr - 300 if "lose" in goal or "похуд" in goal else bmr
    await update.message.reply_text(texts[lang]["cal_result"].format(cal=int(cal)))
    return ConversationHandler.END

# === Handle menu
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    text = update.message.text.lower()

    if "premium" in text or "премиум" in text:
        return await premium(update, context)
    elif "calories" in text or "калории" in text:
        return await calories(update, context)
    elif "plan" in text or "план" in text:
        await update.message.reply_text(texts[lang]["plan_text"])
    elif "progress" in text or "вес" in text:
        await update.message.reply_text(texts[lang]["progress_saved"])
    elif "recipes" in text or "рецепты" in text:
        await update.message.reply_text(texts[lang]["recipe"])
    elif "check" in text or "прив" in text:
        await update.message.reply_text(texts[lang]["checklist"])
    elif "remind" in text or "напо" in text:
        await update.message.reply_text(texts[lang]["reminder_locked"])

# === Launch bot
app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_lang)]},
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("calories", calories)],
    states={
        CAL_W: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_w)],
        CAL_H: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_h)],
        CAL_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_a)],
        CAL_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_g)],
        CAL_Goal: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_goal)],
    },
    fallbacks=[]
))

app.add_handler(CommandHandler("premium", premium))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

print("✅ FitBuddy Balanced Bot is running...")
app.run_polling()
