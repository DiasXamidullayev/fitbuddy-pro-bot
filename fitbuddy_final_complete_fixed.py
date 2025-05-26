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

# Данные
user_progress = {}
user_checklist = {}
premium_users = set()

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я FitBuddy – твой фитнес-консультант 💪\n"
        "Доступные команды:\n"
        "/calories – рассчитать норму калорий\n"
        "/plan – получить план тренировок\n"
        "/remind – создать напоминание\n"
        "/progress – записать вес\n"
        "/recipes – ПП-рецепты\n"
        "/checklist – привычки дня\n"
        "/premium – возможности Premium\n"
        "/confirm – подтверждение оплаты\n"
        "/cancel – отменить\n"
        "/help – помощь"
    )

# === Premium ===
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in premium_users:
        await update.message.reply_text("✅ У тебя уже активирован Premium!")
    else:
        await update.message.reply_text(
            "💎 *Преимущества Premium:*\n"
            "- Умные напоминания\n"
            "- Персональный план\n"
            "- Экспорт веса\n"
            "- Нет ограничений\n\n"
            "💳 Оплата:\n"
            "- Payme: 5614 6835 1617 4125\n"
            "- ZoodPay: https://zoodpay.com/pay/fitbuddy-premium\n\n"
            "После оплаты отправьте /confirm @вашusername",
            parse_mode="Markdown"
        )

# === Подтверждение оплаты ===
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Введите: /confirm @username")
        return
    username = context.args[0].replace("@", "")
    premium_users.add(username)
    await update.message.reply_text(f"✅ Premium активирован для {username}")

# === Остальные команды ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start, /calories, /plan, /remind, /progress, /recipes, /checklist, /cancel")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.")
    return ConversationHandler.END

# === /calories ===
async def calories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи вес (кг):")
    return WEIGHT

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
    if gender not in ['м', 'ж']:
        await update.message.reply_text("Введи 'м' или 'ж'")
        return GENDER
    context.user_data["gender"] = gender
    await update.message.reply_text("Цель? (масса / похудение / поддержание):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ['масса', 'похудение', 'поддержание']:
        await update.message.reply_text("Выбери: масса, похудение, поддержание")
        return GOAL
    w, h, a, g = context.user_data["weight"], context.user_data["height"], context.user_data["age"], context.user_data["gender"]
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g == 'м' else -161)
    calories = bmr + 300 if goal == "масса" else bmr - 300 if goal == "похудение" else bmr
    await update.message.reply_text(f"✅ Суточная норма: {int(calories)} ккал")
    return ConversationHandler.END

# === /plan ===
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Цель? (похудение / масса / поддержание):")
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
    days = int(update.message.text)
    goal, place = context.user_data["goal"], context.user_data["place"]
    plan_text = f"📋 План тренировок ({goal}, {place}, {days}/нед):\n"
    for i in range(1, days + 1):
        if goal == "похудение":
            content = "Кардио + пресс"
        elif goal == "масса":
            content = "Силовая: грудь/спина/ноги"
        else:
            content = "Фуллбоди"
        plan_text += f"День {i}: {content} ({place})\n"
    await update.message.reply_text(plan_text)
    return ConversationHandler.END

# === /remind ===
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что напоминать?")
    return REMIND_TEXT

async def handle_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⏰ Буду напоминать: {update.message.text} (в разработке)")
    return ConversationHandler.END

# === /progress ===
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите вес:")
    return PROGRESS_WEIGHT

async def save_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    weight = float(update.message.text)
    date = datetime.date.today().isoformat()
    if user_id not in user_progress:
        user_progress[user_id] = []
    user_progress[user_id].append((date, weight))
    await update.message.reply_text(f"✅ Вес сохранён: {weight} кг ({date})")
    return ConversationHandler.END

# === /recipes ===
async def recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🥗 Рецепт ПП:\n- Овсянка + банан + орехи = 350 ккал")

# === /checklist ===
async def checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_checklist[update.effective_user.id] = {"вода": False, "тренировка": False}
    await update.message.reply_text("Что сделал: вода / тренировка")
    return CHECKLIST_RESPONSE

async def handle_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id
    if uid not in user_checklist:
        user_checklist[uid] = {"вода": False, "тренировка": False}
    if text in user_checklist[uid]:
        user_checklist[uid][text] = True
    ch = user_checklist[uid]
    await update.message.reply_text(f"💧 Вода: {'✅' if ch['вода'] else '❌'}\n🏋️ Тренировка: {'✅' if ch['тренировка'] else '❌'}")
    return ConversationHandler.END

# === Запуск ===
app = ApplicationBuilder().token("PASTE_YOUR_BOT_TOKEN").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("recipes", recipes))
app.add_handler(CommandHandler("premium", premium))
app.add_handler(CommandHandler("confirm", confirm))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("calories", calories)],
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
    entry_points=[CommandHandler("plan", plan)],
    states={
        PLAN_GOAL: [MessageHandler(filters.TEXT, plan_goal)],
        PLAN_PLACE: [MessageHandler(filters.TEXT, plan_place)],
        PLAN_DAYS: [MessageHandler(filters.TEXT, plan_days)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("remind", remind)],
    states={REMIND_TEXT: [MessageHandler(filters.TEXT, handle_remind)]},
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("progress", progress)],
    states={PROGRESS_WEIGHT: [MessageHandler(filters.TEXT, save_progress)]},
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("checklist", checklist)],
    states={CHECKLIST_RESPONSE: [MessageHandler(filters.TEXT, handle_checklist)]},
    fallbacks=[CommandHandler("cancel", cancel)],
))

print("✅ FitBuddy запущен...")
app.run_polling()
