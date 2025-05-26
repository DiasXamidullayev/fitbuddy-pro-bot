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
user_progress = {}
user_checklist = {}
premium_users = set()

# Главное меню
main_menu = ReplyKeyboardMarkup([
    ["🔥 Калории", "📋 План"],
    ["⚖️ Вес", "⏰ Напоминание"],
    ["🍽️ Рецепты", "✅ Привычки"],
    ["💎 Премиум"]
], resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я FitBuddy.\nВыбери действие:", reply_markup=main_menu)

# === PREMIUM ===
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid in premium_users:
        await update.message.reply_text("✅ У тебя уже Premium.")
    else:
        await update.message.reply_text(
            "💎 Premium включает:\n"
            "- Умные напоминания\n- Персональный план\n- Экспорт веса\n\n"
            "Оплата:\nPayme: 5614 6835 1617 4125\nZoodPay: zoodpay.com/pay/fitbuddy\n"
            "После оплаты: /confirm @username",
            parse_mode="Markdown"
        )

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Используй: /confirm @username")
        return
    username = context.args[0].replace("@", "")
    premium_users.add(username)
    await update.message.reply_text(f"✅ Premium активирован для {username}")

# === КАЛОРИИ ===
async def start_calories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи вес (кг):")
    return WEIGHT

async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["weight"] = float(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return WEIGHT
    await update.message.reply_text("Рост (см):")
    return HEIGHT

async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["height"] = float(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return HEIGHT
    await update.message.reply_text("Возраст:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["age"] = int(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return AGE
    await update.message.reply_text("Пол (м/ж):")
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = update.message.text.lower()
    if g not in ["м", "ж"]:
        await update.message.reply_text("Введи 'м' или 'ж'")
        return GENDER
    context.user_data["gender"] = g
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ["масса", "похудение", "поддержание"]:
        await update.message.reply_text("Выбери: масса, похудение, поддержание")
        return GOAL
    d = context.user_data
    bmr = 10 * d["weight"] + 6.25 * d["height"] - 5 * d["age"] + (5 if d["gender"] == "м" else -161)
    calories = bmr + 300 if goal == "масса" else bmr - 300 if goal == "похудение" else bmr
    await update.message.reply_text(f"✅ Твоя норма: {int(calories)} ккал", reply_markup=main_menu)
    return ConversationHandler.END

# === ПЛАН ===
async def start_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return PLAN_GOAL

async def plan_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text.lower()
    await update.message.reply_text("Где тренируешься? (дом / зал):")
    return PLAN_PLACE

async def plan_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text.lower()
    await update.message.reply_text("Сколько тренировок в неделю?")
    return PLAN_DAYS

async def plan_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return PLAN_DAYS
    g = context.user_data["goal"]
    p = context.user_data["place"]
    plan = f"📋 План ({g}, {p}, {days} дней):\n"
    for i in range(1, days + 1):
        content = "Кардио" if g == "похудение" else "Силовая" if g == "масса" else "Фуллбоди"
        plan += f"День {i}: {content} ({p})\n"
    await update.message.reply_text(plan, reply_markup=main_menu)
    return ConversationHandler.END

# === ВЕС ===
async def start_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи текущий вес (кг):")
    return PROGRESS_WEIGHT

async def save_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return PROGRESS_WEIGHT
    uid = update.effective_user.id
    date = datetime.date.today().isoformat()
    user_progress.setdefault(uid, []).append((date, weight))
    await update.message.reply_text(f"✅ Вес записан: {weight} кг ({date})", reply_markup=main_menu)
    return ConversationHandler.END

# === НАПОМИНАНИЕ ===
async def start_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что напомнить?")
    return REMIND_TEXT

async def save_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⏰ Напоминание (в разработке): {update.message.text}", reply_markup=main_menu)
    return ConversationHandler.END

# === ПРИВЫЧКИ ===
async def start_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_checklist[uid] = {"вода": False, "тренировка": False}
    await update.message.reply_text("Что ты сделал? Напиши: вода / тренировка")
    return CHECKLIST_RESPONSE

async def handle_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id
    if text in user_checklist[uid]:
        user_checklist[uid][text] = True
    ch = user_checklist[uid]
    await update.message.reply_text(f"💧 Вода: {'✅' if ch['вода'] else '❌'}\n🏋️‍♂️ Тренировка: {'✅' if ch['тренировка'] else '❌'}", reply_markup=main_menu)
    return ConversationHandler.END

# === РЕЦЕПТ ===
async def recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍽️ Рецепт: омлет + овощи + зелень = 250 ккал", reply_markup=main_menu)

# === ОБЩИЙ ОБРАБОТЧИК КНОПОК ===
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match update.message.text:
        case "🔥 Калории":
            return await start_calories(update, context)
        case "📋 План":
            return await start_plan(update, context)
        case "⚖️ Вес":
            return await start_progress(update, context)
        case "⏰ Напоминание":
            return await start_reminder(update, context)
        case "✅ Привычки":
            return await start_checklist(update, context)
        case "🍽️ Рецепты":
            return await recipes(update, context)
        case "💎 Премиум":
            return await premium(update, context)
        case _:
            await update.message.reply_text("❗ Выбери из меню.", reply_markup=main_menu)

# === ЗАПУСК ===
app = ApplicationBuilder().token("8079877045:AAFnfzySxIX7OIJXNeIOkhlMH8p0oijQPFA").build()

# Старт и подтверждение
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("confirm", confirm))

# Главное меню
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

# Модули отдельно
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔥 Калории$"), start_calories)],
    states={
        WEIGHT: [MessageHandler(filters.TEXT, get_weight)],
        HEIGHT: [MessageHandler(filters.TEXT, get_height)],
        AGE: [MessageHandler(filters.TEXT, get_age)],
        GENDER: [MessageHandler(filters.TEXT, get_gender)],
        GOAL: [MessageHandler(filters.TEXT, get_goal)],
    },
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📋 План$"), start_plan)],
    states={
        PLAN_GOAL: [MessageHandler(filters.TEXT, plan_goal)],
        PLAN_PLACE: [MessageHandler(filters.TEXT, plan_place)],
        PLAN_DAYS: [MessageHandler(filters.TEXT, plan_days)],
    },
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⚖️ Вес$"), start_progress)],
    states={PROGRESS_WEIGHT: [MessageHandler(filters.TEXT, save_progress)]},
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⏰ Напоминание$"), start_reminder)],
    states={REMIND_TEXT: [MessageHandler(filters.TEXT, save_reminder)]},
    fallbacks=[]
))

app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^✅ Привычки$"), start_checklist)],
    states={CHECKLIST_RESPONSE: [MessageHandler(filters.TEXT, handle_checklist)]},
    fallbacks=[]
))

print("✅ FitBuddy модульно запущен")
app.run_polling()
