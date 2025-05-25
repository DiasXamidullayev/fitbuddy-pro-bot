
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
        "start": "👋 Welcome to FitBuddy! Choose your language:",
        "menu": "🏋️‍♂️ Main Menu — choose an action:",
        "already_premium": "💎 You already have Premium access.",
        "premium_ad": "💎 *Premium Features Include:*

"
                      "• Smart workout reminders
"
                      "• Export progress to PDF
"
                      "• Unlimited weight tracking
"
                      "• Personalized calorie plans

"
                      "*To activate Premium:*
"
                      "🌍 ZoodPay: https://zoodpay.com/pay/fitbuddy-premium
"
                      "🇺🇿 Payme: 5614 6835 1617 4125 (Xamidullayev Dias)

"
                      "Send payment screenshot to unlock access.",
        "not_premium": "🚫 This is a Premium-only feature. Use /premium to upgrade.",
        "cal_q1": "Enter your weight (kg):",
        "cal_q2": "Now your height (cm):",
        "cal_q3": "Your age:",
        "cal_q4": "Gender (m/f):",
        "cal_q5": "Goal? (gain / lose / maintain):",
        "cal_result": "✅ Your daily calorie need: {cal} kcal",
        "plan": "📆 Weekly Plan:
Mon - Cardio
Wed - Strength
Fri - Core + Stretch",
        "progress": "✅ Weight saved!",
        "recipe": "🍽️ Try: oats + banana + peanut butter (~350 kcal)",
        "checklist": "✅ Daily Checklist: water? workout?",
        "reminder_promo": "⏰ Premium reminders help you stay consistent.
Use /premium to unlock."
    },
    "ru": {
        "start": "👋 Добро пожаловать в FitBuddy! Выберите язык:",
        "menu": "🏋️ Главное меню — выберите действие:",
        "already_premium": "💎 У вас уже есть Premium-доступ.",
        "premium_ad": "💎 *Преимущества Premium:*

"
                      "• Умные напоминания о тренировках
"
                      "• Экспорт прогресса в PDF
"
                      "• Неограниченная история веса
"
                      "• Персонализированный план калорий

"
                      "*Как активировать Premium:*
"
                      "🌍 ZoodPay: https://zoodpay.com/pay/fitbuddy-premium
"
                      "🇺🇿 Payme: 5614 6835 1617 4125 (Xamidullayev Dias)

"
                      "После оплаты отправьте скриншот — мы откроем доступ.",
        "not_premium": "🚫 Эта функция доступна только в Premium. Введите /premium для обновления.",
        "cal_q1": "Введите ваш вес (кг):",
        "cal_q2": "Теперь ваш рост (см):",
        "cal_q3": "Возраст:",
        "cal_q4": "Пол (м/ж):",
        "cal_q5": "Цель? (набор / похудение / поддержание):",
        "cal_result": "✅ Ваша дневная норма калорий: {cal} ккал",
        "plan": "📆 План на неделю:
Пн - Кардио
Ср - Силовая
Пт - Кор + Растяжка",
        "progress": "✅ Вес сохранён!",
        "recipe": "🍽️ Попробуйте: овсянка + банан + арахис (~350 ккал)",
        "checklist": "✅ Чеклист: вода? тренировка?",
        "reminder_promo": "⏰ Умные напоминания доступны в Premium.
Введите /premium для доступа."
    }
}

lang_buttons = ReplyKeyboardMarkup(
    [[KeyboardButton("English"), KeyboardButton("Русский")]],
    resize_keyboard=True
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
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    await update.message.reply_text(texts[lang]["start"], reply_markup=lang_buttons)
    return LANGUAGE

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = "en" if update.message.text.lower() == "english" else "ru"
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
        await update.message.reply_text("❗ Use /confirm @username")
        return
    target_username = context.args[0].lstrip("@")
    target_id = user_names.get(f"@{target_username}")
    if target_id:
        premium_users[target_id] = True
        save(PREMIUM_FILE, premium_users)
        await update.message.reply_text(f"✅ Premium activated for {target_username}")
        await context.bot.send_message(chat_id=target_id, text="💎 Premium activated. Thank you!")
    else:
        await update.message.reply_text("❗ User not found or not started the bot.")

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_names[f"@{update.effective_user.username}"] = user_id
    lang = user_lang.get(user_id, "en")
    msg = update.message.text

    if msg in ["📆 Plan", "План"]:
        await update.message.reply_text(texts[lang]["plan"])
    elif msg in ["📈 Weight", "Вес"]:
        await update.message.reply_text(texts[lang]["progress"])
    elif msg in ["🍲 Recipes", "Рецепты"]:
        await update.message.reply_text(texts[lang]["recipe"])
    elif msg in ["✅ Habits", "Привычки"]:
        await update.message.reply_text(texts[lang]["checklist"])
    elif msg in ["⏰ Reminders", "Напоминание"]:
        await update.message.reply_text(texts[lang]["reminder_promo"])
    elif msg in ["💎 Premium", "Премиум"]:
        await premium(update, context)
    elif msg in ["🔥 Calories", "Калории"]:
        await update.message.reply_text(texts[lang]["cal_q1"])
        return CAL_W

    return ConversationHandler.END

async def calories_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    context.user_data["weight"] = float(update.message.text)
    await update.message.reply_text(texts[lang]["cal_q2"])
    return CAL_H

async def cal_h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    context.user_data["height"] = float(update.message.text)
    await update.message.reply_text(texts[lang]["cal_q3"])
    return CAL_A

async def cal_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    context.user_data["age"] = int(update.message.text)
    await update.message.reply_text(texts[lang]["cal_q4"])
    return CAL_G

async def cal_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts[user_lang.get(str(update.effective_user.id), "en")]["cal_q5"])
    context.user_data["gender"] = update.message.text.lower()
    return CAL_Goal

async def cal_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    goal = update.message.text.lower()
    cal = 10 * data["weight"] + 6.25 * data["height"] - 5 * data["age"]
    cal += 5 if data["gender"] == "m" else -161
    if goal == "gain" or goal == "набор": cal += 300
    elif goal == "lose" or goal == "похудение": cal -= 300
    lang = user_lang.get(str(update.effective_user.id), "en")
    await update.message.reply_text(texts[lang]["cal_result"].format(cal=int(cal)))
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token("8079877045:AAFW4YjWO9plFtC8FoV4_G_W1K_SgAlIwYw").build()
    lang_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_lang)]},
        fallbacks=[]
    )
    cal_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handler)],
        states={
            CAL_W: [MessageHandler(filters.TEXT & ~filters.COMMAND, calories_step)],
            CAL_H: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_h)],
            CAL_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_a)],
            CAL_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_g)],
            CAL_Goal: [MessageHandler(filters.TEXT & ~filters.COMMAND, cal_goal)],
        },
        fallbacks=[]
    )

    app.add_handler(lang_conv)
    app.add_handler(cal_conv)
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("confirm", confirm))
    app.run_polling()
