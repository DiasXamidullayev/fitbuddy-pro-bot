from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
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
    await update.message.reply_text(
        "👋 Привет! Я FitBuddy — твой фитнес-бот.\nВыбери действие:",
        reply_markup=main_menu
    )

# Premium реклама
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid in premium_users:
        await update.message.reply_text("✅ У тебя уже Premium-доступ.")
    else:
        await update.message.reply_text(
            "💎 *Преимущества Premium:*\n"
            "- Умные напоминания\n- Экспорт прогресса\n- Персональные планы\n\n"
            "Оплата:\nPayme: 5614 6835 1617 4125\nZoodPay: https://zoodpay.com/pay/fitbuddy\n\n"
            "После оплаты: /confirm @username",
            parse_mode="Markdown"
        )

# /confirm
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Введите /confirm @username")
        return
    username = context.args[0].replace("@", "")
    premium_users.add(username)
    await update.message.reply_text(f"✅ Premium активирован для {username}")

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
        await update.message.reply_text("Введите 'м' или 'ж'")
        return GENDER
    context.user_data["gender"] = g
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ['масса', 'похудение', 'поддержание']:
        await update.message.reply_text("Выберите: масса, похудение, поддержание")
        return GOAL
    w, h, a, g = context.user_data["weight"], context.user_data["height"], context.user_data["age"], context.user_data["gender"]
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g == 'м' else -161)
    cal = bmr + 300 if goal == "масса" else bmr - 300 if goal == "похудение" else bmr
    await update.message.reply_text(f"✅ Твоя норма: {int(cal)} ккал", reply_markup=main_menu)
    return ConversationHandler.END

# === План ===
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
        block = "Кардио" if g == "похудение" else "Силовая" if g == "масса" else "Фуллбоди"
        plan += f"День {i}: {block} ({p})\n"
    await update.message.reply_text(plan, reply_markup=main_menu)
    return ConversationHandler.END

# === Вес ===
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

# === Напоминания ===
async def handle_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"⏰ Напоминание установлено (в будущем): {text}", reply_markup=main_menu)
    return ConversationHandler.END

# === Чеклист ===
async def handle_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id
    if uid not in user_checklist:
        user_checklist[uid] = {"вода": False, "тренировка": False}
    if text in user_checklist[uid]:
        user_checklist[uid][text] = True
    ch = user_checklist[uid]
    await update.message.reply_text(f"💧 Вода: {'✅' if ch['вода'] else '❌'}\n🏋️‍♂️ Тренировка: {'✅' if ch['тренировка'] else '❌'}", reply_markup=main_menu)
    return ConversationHandler.END

# === Recipes ===
async def recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍽️ Овсянка + банан + орехи = 350 ккал", reply_markup=main_menu)

# === Обработка кнопок ===
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔥 Калории":
        await update.message.reply_text("Введи вес (кг):")
        return WEIGHT
    elif text == "📋 План":
        await update.message.reply_text("Цель? (похудение / масса / поддержание):")
        return PLAN_GOAL
    elif text == "⚖️ Вес":
        await update.message.reply_text("Введи текущий вес (кг):")
        return PROGRESS_WEIGHT
    elif text == "⏰ Напоминание":
        await update.message.reply_text("Что напоминать?")
        return REMIND_TEXT
    elif text == "🍽️ Рецепты":
        return await recipes(update, context)
    elif text == "✅ Привычки":
        uid = update.effective_user.id
        user_checklist[uid] = {"вода": False, "тренировка": False}
        await update.message.reply_text("Напиши: вода / тренировка")
        return CHECKLIST_RESPONSE
    elif text == "💎 Премиум":
        return await premium(update, context)

# === Запуск ===
app = ApplicationBuilder().token("8079877045:AAHY2DN0aI_zsDNLtt9D1kNP88rJ_SCgPXc").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(MessageHandler(filters.Regex("^(🔥 Калории|📋 План|⚖️ Вес|⏰ Напоминание|🍽️ Рецепты|✅ Привычки|💎 Премиум)$"), handle_buttons))

# Calories
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔥 Калории$"), handle_buttons)],
    states={
        WEIGHT: [MessageHandler(filters.TEXT, get_weight)],
        HEIGHT: [MessageHandler(filters.TEXT, get_height)],
        AGE: [MessageHandler(filters.TEXT, get_age)],
        GENDER: [MessageHandler(filters.TEXT, get_gender)],
        GOAL: [MessageHandler(filters.TEXT, get_goal)],
    },
    fallbacks=[]
))

# Plan
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📋 План$"), handle_buttons)],
    states={
        PLAN_GOAL: [MessageHandler(filters.TEXT, plan_goal)],
        PLAN_PLACE: [MessageHandler(filters.TEXT, plan_place)],
        PLAN_DAYS: [MessageHandler(filters.TEXT, plan_days)],
    },
    fallbacks=[]
))

# Progress
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⚖️ Вес$"), handle_buttons)],
    states={PROGRESS_WEIGHT: [MessageHandler(filters.TEXT, save_progress)]},
    fallbacks=[]
))

# Reminder
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^⏰ Напоминание$"), handle_buttons)],
    states={REMIND_TEXT: [MessageHandler(filters.TEXT, handle_remind)]},
    fallbacks=[]
))

# Checklist
app.add_handler(ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^✅ Привычки$"), handle_buttons)],
    states={CHECKLIST_RESPONSE: [MessageHandler(filters.TEXT, handle_checklist)]},
    fallbacks=[]
))

print("✅ FitBuddy запущен")
app.run_polling()
