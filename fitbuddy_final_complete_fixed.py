from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
import datetime

# Состояния
WEIGHT, HEIGHT, AGE, GENDER, GOAL = range(5)
PLAN_GOAL, PLAN_PLACE, PLAN_DAYS = range(10, 13)
REMIND_TEXT = 20
PROGRESS_WEIGHT = 30
CHECKLIST_RESPONSE = 40

# Хранилища
user_lang = {}
user_progress = {}
user_checklist = {}
premium_users = set()

# Кнопки
main_menu = ReplyKeyboardMarkup(
    [
        ["🔥 Калории", "📆 План"],
        ["📈 Вес", "🍽️ Рецепты"],
        ["✅ Привычки", "⏰ Напоминание"],
        ["💎 Премиум"]
    ],
    resize_keyboard=True
)

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_lang[user_id] = "ru"
    await update.message.reply_text(
        "👋 Привет! Я FitBuddy – твой фитнес-консультант. Выбери действие:",
        reply_markup=main_menu
    )

# === ОБРАБОТКА КНОПОК ===
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔥 Калории":
        await update.message.reply_text("Введи вес (кг):")
        return WEIGHT
    elif text == "📆 План":
        await update.message.reply_text("Цель? (похудение / масса / поддержание):")
        return PLAN_GOAL
    elif text == "📈 Вес":
        await update.message.reply_text("Введи текущий вес:")
        return PROGRESS_WEIGHT
    elif text == "🍽️ Рецепты":
        await update.message.reply_text("🥗 Рецепт ПП: овсянка + банан + орехи = 350 ккал")
    elif text == "✅ Привычки":
        uid = update.effective_user.id
        user_checklist[uid] = {"вода": False, "тренировка": False}
        await update.message.reply_text("Что ты сделал сегодня? вода / тренировка")
        return CHECKLIST_RESPONSE
    elif text == "⏰ Напоминание":
        await update.message.reply_text("Что напоминать?")
        return REMIND_TEXT
    elif text == "💎 Премиум":
        uid = str(update.effective_user.id)
        if uid in premium_users:
            await update.message.reply_text("✅ У тебя уже есть доступ Premium.")
        else:
            await update.message.reply_text(
                "💎 Premium:\n"
                "- Напоминания\n- Экспорт\n- Персональные планы\n\n"
                "Оплата:\nPayme: 5614 6835 1617 4125\nZoodPay: zoodpay.com/pay/fitbuddy\n\n"
                "После оплаты напиши /confirm @username",
                parse_mode="Markdown"
            )

# === PREMIUM CONFIRM ===
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введи: /confirm @username")
        return
    username = context.args[0].replace("@", "")
    premium_users.add(username)
    await update.message.reply_text(f"✅ Premium активирован для {username}")

# === CALORIES ===
async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = float(update.message.text)
    await update.message.reply_text("Рост (см):")
    return HEIGHT

async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["height"] = float(update.message.text)
    await update.message.reply_text("Возраст:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = int(update.message.text)
    await update.message.reply_text("Пол (м/ж):")
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text.lower()
    if gender not in ["м", "ж"]:
        await update.message.reply_text("Введи м или ж")
        return GENDER
    context.user_data["gender"] = gender
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    w, h, a, g = context.user_data["weight"], context.user_data["height"], context.user_data["age"], context.user_data["gender"]
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g == "м" else -161)
    cal = bmr + 300 if goal == "масса" else bmr - 300 if goal == "похудение" else bmr
    await update.message.reply_text(f"✅ Твоя норма: {int(cal)} ккал")
    return ConversationHandler.END

# === PLAN ===
async def plan_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text.lower()
    await update.message.reply_text("Где тренироваться? (дом / зал):")
    return PLAN_PLACE

async def plan_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text.lower()
    await update.message.reply_text("Сколько дней в неделю тренируешься?")
    return PLAN_DAYS

async def plan_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days = int(update.message.text)
    goal = context.user_data["goal"]
    place = context.user_data["place"]
    plan = f"📋 План ({goal}, {place}, {days} дн):\n"
    for i in range(1, days + 1):
        if goal == "масса":
            content = "Силовая"
        elif goal == "похудение":
            content = "Кардио"
        else:
            content = "Фуллбоди"
        plan += f"День {i}: {content} ({place})\n"
    await update.message.reply_text(plan)
    return ConversationHandler.END

# === REMINDER ===
async def handle_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⏰ Напоминание установлено: {update.message.text} (в разработке)")
    return ConversationHandler.END

# === PROGRESS ===
async def save_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    weight = float(update.message.text)
    date = datetime.date.today().isoformat()
    if uid not in user_progress:
        user_progress[uid] = []
    user_progress[uid].append((date, weight))
    await update.message.reply_text(f"✅ Вес {weight} кг сохранён ({date})")
    return ConversationHandler.END

# === CHECKLIST ===
async def handle_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id
    if uid not in user_checklist:
        user_checklist[uid] = {"вода": False, "тренировка": False}
    if text in user_checklist[uid]:
        user_checklist[uid][text] = True
    ch = user_checklist[uid]
    await update.message.reply_text(f"💧 Вода: {'✅' if ch['вода'] else '❌'}\n🏋️‍♂️ Тренировка: {'✅' if ch['тренировка'] else '❌'}")
    return ConversationHandler.END

# === CANCEL ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.")
    return ConversationHandler.END

# === ЗАПУСК ===
app = ApplicationBuilder().token("8079877045:AAFW4YjWO9plFtC8FoV4_G_W1K_SgAlIwYw").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("confirm", confirm))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔥 Калории$"), handle_button)],
    states={
        WEIGHT: [MessageHandler(filters.TEXT, get_weight)],
        HEIGHT: [MessageHandler(filters.TEXT, get_height)],
        AGE: [MessageHandler(filters.TEXT, get_age)],
        GENDER: [MessageHandler(filters.TEXT, get_gender)],
        GOAL: [MessageHandler(filters.TEXT, get_goal)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📆 План$"), handle_button)],
    states={
        PLAN_GOAL: [MessageHandler(filters.TEXT, plan_goal)],
        PLAN_PLACE: [MessageHandler(filters.TEXT, plan_place)],
        PLAN_DAYS: [MessageHandler(filters.TEXT, plan_days)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📈 Вес$"), handle_button)],
    states={
        PROGRESS_WEIGHT: [MessageHandler(filters.TEXT, save_progress)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^✅ Привычки$"), handle_button)],
    states={
        CHECKLIST_RESPONSE: [MessageHandler(filters.TEXT, handle_checklist)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⏰ Напоминание$"), handle_button)],
    states={
        REMIND_TEXT: [MessageHandler(filters.TEXT, handle_remind)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(MessageHandler(filters.Regex("^(🍽️ Рецепты|💎 Премиум)$"), handle_button))

print("✅ Бот с кнопками запущен")
app.run_polling()
