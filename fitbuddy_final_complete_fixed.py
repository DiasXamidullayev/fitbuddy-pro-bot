from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
import datetime

# Состояния
MENU, WEIGHT, HEIGHT, AGE, GENDER, GOAL = range(6)
PLAN_GOAL, PLAN_PLACE, PLAN_DAYS = range(10, 13)
REMIND_TEXT = 20
PROGRESS_WEIGHT = 30
CHECKLIST_RESPONSE = 40

# Хранилища
user_progress = {}
user_checklist = {}
premium_users = set()

# Главное меню
menu_keyboard = ReplyKeyboardMarkup([
    ["🔥 Калории", "📋 План"],
    ["⚖️ Вес", "⏰ Напоминание"],
    ["🍽️ Рецепты", "✅ Привычки"],
    ["💎 Премиум"]
], resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Добро пожаловать в FitBuddy!\nВыбери действие:", reply_markup=menu_keyboard)
    return MENU

# /confirm
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши /confirm @username")
        return
    username = context.args[0].replace("@", "")
    premium_users.add(username)
    await update.message.reply_text(f"✅ Premium активирован для {username}")

# Главное меню
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("Что тебе напоминать?")
        return REMIND_TEXT

    elif text == "🍽️ Рецепты":
        await update.message.reply_text("🥗 Овсянка + банан + орехи = 350 ккал")
        return MENU

    elif text == "✅ Привычки":
        uid = update.effective_user.id
        user_checklist[uid] = {"вода": False, "тренировка": False}
        await update.message.reply_text("Что сделал? Напиши: вода / тренировка")
        return CHECKLIST_RESPONSE

    elif text == "💎 Премиум":
        uid = str(update.effective_user.id)
        if uid in premium_users:
            await update.message.reply_text("✅ У тебя уже есть Premium.")
        else:
            await update.message.reply_text(
                "💎 *Premium-возможности:*\n"
                "- Напоминания\n- Персональные планы\n- Экспорт прогресса\n\n"
                "Оплата:\nPayme: 5614 6835 1617 4125\nZoodPay: https://zoodpay.com/pay/fitbuddy\n"
                "После оплаты: /confirm @username",
                parse_mode="Markdown"
            )
        return MENU

    else:
        await update.message.reply_text("Выбери кнопку из меню.")
        return MENU

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
    gender = update.message.text.lower()
    if gender not in ["м", "ж"]:
        await update.message.reply_text("Введи 'м' или 'ж'")
        return GENDER
    context.user_data["gender"] = gender
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ["масса", "похудение", "поддержание"]:
        await update.message.reply_text("Выберите цель.")
        return GOAL
    d = context.user_data
    bmr = 10 * d["weight"] + 6.25 * d["height"] - 5 * d["age"] + (5 if d["gender"] == 'м' else -161)
    result = bmr + 300 if goal == "масса" else bmr - 300 if goal == "похудение" else bmr
    await update.message.reply_text(f"✅ Твоя суточная норма: {int(result)} ккал", reply_markup=menu_keyboard)
    return MENU

# === План ===
async def get_plan_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text.lower()
    await update.message.reply_text("Где тренируешься? (дом / зал):")
    return PLAN_PLACE

async def get_plan_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text.lower()
    await update.message.reply_text("Сколько дней в неделю тренируешься?")
    return PLAN_DAYS

async def get_plan_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return PLAN_DAYS
    g = context.user_data["goal"]
    p = context.user_data["place"]
    msg = f"📋 План ({g}, {p}, {days} дней):\n"
    for i in range(1, days + 1):
        block = "Кардио" if g == "похудение" else "Силовая" if g == "масса" else "Фуллбоди"
        msg += f"День {i}: {block} ({p})\n"
    await update.message.reply_text(msg, reply_markup=menu_keyboard)
    return MENU

# === Вес ===
async def save_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
    except:
        await update.message.reply_text("Введите число.")
        return PROGRESS_WEIGHT
    uid = update.effective_user.id
    date = datetime.date.today().isoformat()
    user_progress.setdefault(uid, []).append((date, weight))
    await update.message.reply_text(f"✅ Вес сохранён: {weight} кг ({date})", reply_markup=menu_keyboard)
    return MENU

# === Напоминание ===
async def save_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⏰ Напоминание сохранено (пока не реализовано): {update.message.text}", reply_markup=menu_keyboard)
    return MENU

# === Привычки ===
async def checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id
    if uid not in user_checklist:
        user_checklist[uid] = {"вода": False, "тренировка": False}
    if text in user_checklist[uid]:
        user_checklist[uid][text] = True
    d = user_checklist[uid]
    await update.message.reply_text(
        f"💧 Вода: {'✅' if d['вода'] else '❌'}\n🏋️‍♂️ Тренировка: {'✅' if d['тренировка'] else '❌'}",
        reply_markup=menu_keyboard
    )
    return MENU

# === Отмена ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=menu_keyboard)
    return MENU

# === Запуск ===
app = ApplicationBuilder().token("8079877045:AAGycBqKchETAqCigVcT0Vgz0rXoq8-swpI").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("confirm", confirm))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
        WEIGHT: [MessageHandler(filters.TEXT, get_weight)],
        HEIGHT: [MessageHandler(filters.TEXT, get_height)],
        AGE: [MessageHandler(filters.TEXT, get_age)],
        GENDER: [MessageHandler(filters.TEXT, get_gender)],
        GOAL: [MessageHandler(filters.TEXT, get_goal)],
        PLAN_GOAL: [MessageHandler(filters.TEXT, get_plan_goal)],
        PLAN_PLACE: [MessageHandler(filters.TEXT, get_plan_place)],
        PLAN_DAYS: [MessageHandler(filters.TEXT, get_plan_days)],
        PROGRESS_WEIGHT: [MessageHandler(filters.TEXT, save_weight)],
        REMIND_TEXT: [MessageHandler(filters.TEXT, save_reminder)],
        CHECKLIST_RESPONSE: [MessageHandler(filters.TEXT, checklist)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
))

print("✅ FitBuddy запущен")
app.run_polling()
