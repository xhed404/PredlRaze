import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TOKEN = '8180948994:AAHaZX-U1WPE2gtZ2aPWw8Ca_isHMSqif9I'
ADMIN_ID = 5140455624

logging.basicConfig(level=logging.INFO)

submission_enabled = True
user_submissions = {}
submitted_in_cycle = set()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Отправь 3 свои работы (фото), чтобы предложить их для ДИЗАЙНИК'а.\n"
        "❗ Сейчас статус подачи: " + ("✅ открыт" if submission_enabled else "🚫 закрыт")
    )

def enable_submissions(update: Update, context: CallbackContext):
    global submission_enabled, submitted_in_cycle, user_submissions
    if update.effective_user.id != ADMIN_ID:
        return
    submission_enabled = True
    submitted_in_cycle.clear()
    user_submissions.clear()
    update.message.reply_text("✅ Приём заявок снова открыт!")

def disable_submissions(update: Update, context: CallbackContext):
    global submission_enabled
    if update.effective_user.id != ADMIN_ID:
        return
    submission_enabled = False
    update.message.reply_text("🚫 Приём заявок закрыт. Новые работы отправлять нельзя.")

def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "пользователь"

    if not submission_enabled:
        update.message.reply_text("❌ Приём заявок сейчас закрыт. Пожалуйста, попробуй позже.")
        return

    if user_id in submitted_in_cycle:
        update.message.reply_text("⏳ Ты уже отправлял 3 работы в этом НАБОРЕ. Жди следующего набора.")
        return

    photo = update.message.photo[-1].file_id
    if user_id not in user_submissions:
        user_submissions[user_id] = []

    user_submissions[user_id].append(photo)

    if len(user_submissions[user_id]) == 3:
        media_group = [InputMediaPhoto(file_id) for file_id in user_submissions[user_id]]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user_id}")],
            [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")]
        ])

        context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 Новая заявка от @{username}")
        context.bot.send_media_group(chat_id=ADMIN_ID, media=media_group)
        context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=keyboard)

        update.message.reply_text("✅ Работы отправлены. Жди ответа от @razesigm.")
        submitted_in_cycle.add(user_id)
    else:
        update.message.reply_text(f"Фото {len(user_submissions[user_id])}/3 принято. Осталось {3 - len(user_submissions[user_id])}.")

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith("approve_") or data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        approved = data.startswith("approve")

        msg = "🎉 Твои работы одобрены!" if approved else "❌ К сожалению, твои работы отклонены."
        result = "✅ Одобрено." if approved else "❌ Отклонено."

        context.bot.send_message(chat_id=user_id, text=msg)
        query.edit_message_text(result)

        user_submissions.pop(user_id, None)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("open", enable_submissions))
    dp.add_handler(CommandHandler("close", disable_submissions))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(CallbackQueryHandler(handle_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


