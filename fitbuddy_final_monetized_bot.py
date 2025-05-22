from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
LANGUAGE, CAL_W, CAL_H, CAL_A, CAL_G, CAL_Goal = range(6)
user_names = {}  # username -> user_id
# === Старт и язык ===
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

# === Premium доступ и реклама ===
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    lang = user_lang.get(user_id, "en")
    if user_id in premium_users:
        await update.message.reply_text(texts[lang]["already_premium"])
    else:
        await update.message.reply_text(texts[lang]["premium_ad"], parse_mode="Markdown")

# === Команда подтверждения оплаты ===
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи имя пользователя, например: /confirm @username")
        return
    target_username = context.args[0]
    target_id = user_names.get(target_username)
    if target_id:
        premium_users[target_id] = True
        save(PREMIUM_FILE, premium_users)
        await update.message.reply_text(f"✅ Premium активирован для {target_username}")
        await context.bot.send_message(chat_id=target_id, text="💎 Вам активирован Premium-доступ. Спасибо за оплату!")
    else:
        await update.message.reply_text("❌ Пользователь не найден. Он должен сначала написать боту.")

# === Калькулятор калорий ===
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
    w, h, a, g = context.user_data["w"], context.user_data["h"], context.user_data["a"], context.user_data["g"]
    lang = user_lang.get(str(update.effective_user.id), "en")
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g.startswith("m") or g == "м" else -161)
    cal = bmr + 300 if "gain" in goal or "масса" in goal else bmr - 300 if "lose" in goal or "похуд" in goal else bmr
    await update.message.reply_text(texts[lang]["cal_result"].format(cal=int(cal)))
    return ConversationHandler.END

# === Обработка кнопок ===
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    if username:
        user_names[f"@{username}"] = user_id

    lang = user_lang.get(user_id, "en")
    text = update.message.text.lower()

    if "premium" in text or "премиум" in text:
        return await premium(update, context)
    elif "cal" in text or "кал" in text:
        return await calories(update, context)
    elif "plan" in text or "план" in text:
        await update.message.reply_text(texts[lang]["plan"])
    elif "progress" in text or "вес" in text:
        await update.message.reply_text(texts[lang]["progress"])
    elif "recip" in text or "рец" in text:
        await update.message.reply_text(texts[lang]["recipe"])
    elif "check" in text or "прив" in text:
        await update.message.reply_text(texts[lang]["checklist"])
    elif "remind" in text or "напо" in text:
        await update.message.reply_text(texts[lang]["reminder_promo"])

# === Запуск бота ===
app = ApplicationBuilder().token("7732210436:AAEpp7YiQnGMghdWar0PvHU_0fb2IF7Qf6Q").build()

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
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

print("🚀 FitBuddy Premium bot is running...")
app.run_polling()
