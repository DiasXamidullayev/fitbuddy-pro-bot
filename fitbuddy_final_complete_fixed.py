from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
import datetime

# === Состояния ===
WEIGHT, HEIGHT, AGE, GENDER, GOAL = range(5)
PLAN_GOAL, PLAN_PLACE, PLAN_DAYS = range(10, 13)
REMIND_TEXT = 20
PROGRESS_WEIGHT = 30
CHECKLIST_RESPONSE = 40

user_progress = {}
user_checklist = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[["🔥 Калории", "📋 План"], ["⏰ Напоминание", "📈 Вес"], ["🍽️ Рецепты", "✅ Привычки"]],
    resize_keyboard=True
)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я FitBuddy – твой фитнес-помощник!\n"
        "Выбери действие снизу ⬇️",
        reply_markup=main_menu
    )

# === Обработка текста-кнопок ===
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔥 Калории":
        await update.message.reply_text("Введи вес (кг):")
        return WEIGHT
    elif text == "📋 План":
        await update.message.reply_text("Цель? (похудение / масса / поддержание):")
        return PLAN_GOAL
    elif text == "⏰ Напоминание":
        await update.message.reply_text("Что тебе напоминать?")
        return REMIND_TEXT
    elif text == "📈 Вес":
        await update.message.reply_text("Введи текущий вес (кг):")
        return PROGRESS_WEIGHT
    elif text == "🍽️ Рецепты":
        await update.message.reply_text("🥗 Омлет с овощами: 2 яйца, перец, помидор, зелень.")
    elif text == "✅ Привычки":
        user_checklist[update.effective_user.id] = {"вода": False, "тренировка": False}
        await update.message.reply_text("Что ты выполнил? (вода / тренировка)")
        return CHECKLIST_RESPONSE

# === Калории ===
async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["weight"] = float(update.message.text)
        await update.message.reply_text("Рост (см):")
        return HEIGHT
    except:
        await update.message.reply_text("Введите число.")
        return WEIGHT

async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["height"] = float(update.message.text)
        await update.message.reply_text("Возраст:")
        return AGE
    except:
        await update.message.reply_text("Введите число.")
        return HEIGHT

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["age"] = int(update.message.text)
        await update.message.reply_text("Пол (м/ж):")
        return GENDER
    except:
        await update.message.reply_text("Введите число.")
        return AGE

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = update.message.text.lower()
    if g not in ['м', 'ж']:
        await update.message.reply_text("Введи 'м' или 'ж'")
        return GENDER
    context.user_data["gender"] = g
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ['масса', 'похудение', 'поддержание']:
        await update.message.reply_text("Выберите: масса, похудение, поддержание.")
        return GOAL

    w = context.user_data["weight"]
    h = context.user_data["height"]
    a = context.user_data["age"]
    g = context.user_data["gender"]
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g == 'м' else -161)

    if goal == "масса":
        calories = bmr + 300
    elif goal == "похудение":
        calories = bmr - 300
    else:
        calories = bmr

    await update.message.reply_text(f"Твоя суточная норма: {int(calories)} ккал.")
    return ConversationHandler.END

# === План ===
async def plan_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ['похудение', 'масса', 'поддержание']:
        await update.message.reply_text("Выбери: похудение, масса, поддержание.")
        return PLAN_GOAL
    context.user_data["goal"] = goal
    await update.message.reply_text("Где тренируешься? (дом / зал):")
    return PLAN_PLACE

async def plan_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text.lower()
    if place not in ['дом', 'зал']:
        await update.message.reply_text("Выбери: дом или зал.")
        return PLAN_PLACE
    context.user_data["place"] = place
    await update.message.reply_text("Сколько тренировок в неделю?")
    return PLAN_DAYS

async def plan_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text)
    except:
        await update.message.reply_text("Введи число.")
        return PLAN_DAYS

    goal = context.user_data["goal"]
    place = context.user_data["place"]
    text = f"📋 План тренировок ({goal}, {place}, {days} дней):\n"
    for i in range(1, days + 1):
        content = "Кардио" if goal == "похудение" else "Силовая" if goal == "масса" else "Комбинированная"
        text += f"День {i}: {content} ({place})\n"
    await update.message.reply_text(text)
    return ConversationHandler.END

# === Прочие ===
async def handle_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Буду напоминать: '{text}' (в будущем).")
    return ConversationHandler.END

async def save_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return PROGRESS_WEIGHT
    uid = update.effective_user.id
    date = datetime.date.today().isoformat()
    user_progress.setdefault(uid, []).append((date, weight))
    await update.message.reply_text(f"✅ Записано: {weight} кг ({date})")
    return ConversationHandler.END

async def handle_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id
    if uid not in user_checklist:
        user_checklist[uid] = {"вода": False, "тренировка": False}
    if text in user_checklist[uid]:
        user_checklist[uid][text] = True
    cl = user_checklist[uid]
    await update.message.reply_text(
        f"Прогресс дня:\n💧 Вода: {'✅' if cl['вода'] else '❌'}\n🏋️‍♂️ Тренировка: {'✅' if cl['тренировка'] else '❌'}"
    )
    return ConversationHandler.END

# === Запуск ===
app = ApplicationBuilder().token("8079877045:AAGsksKjDXs22kSu1nJOkY4J8F44Zij4N_s").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# Все ветки
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔥 Калории$"), handle_buttons)],
    states={
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
    },
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📋 План$"), handle_buttons)],
    states={
        PLAN_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_goal)],
        PLAN_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_place)],
        PLAN_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_days)],
    },
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⏰ Напоминание$"), handle_buttons)],
    states={REMIND_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remind)]},
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📈 Вес$"), handle_buttons)],
    states={PROGRESS_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_progress)]},
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^✅ Привычки$"), handle_buttons)],
    states={CHECKLIST_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_checklist)]},
    fallbacks=[]
))

print("✅ Бот запущен.")
app.run_polling()
