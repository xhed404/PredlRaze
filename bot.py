import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TOKEN = '8180948994:AAHaZX-U1WPE2gtZ2aPWw8Ca_isHMSqif9I'
ADMIN_ID = 6458164021

logging.basicConfig(level=logging.INFO)
user_submissions = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Если ты попал в этого бота, значит ты хочешь предложить свои фото в нашего бота — Дизайник'а.\n\n"
        "📸 Пожалуйста, отправь сюда 3 ФОТО (свои работы), и @razesigm возможно добавит их в бота. После жди ответа."
    )

def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1].file_id

    if user_id not in user_submissions:
        user_submissions[user_id] = []

    user_submissions[user_id].append(photo)

    if len(user_submissions[user_id]) == 3:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Одобрить работы", callback_data=f"approve_{user_id}")],
            [InlineKeyboardButton("❌ Не одобрить работы", callback_data=f"reject_{user_id}")]
        ])
        media_group = [InputMediaPhoto(file_id) for file_id in user_submissions[user_id]]

        context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 Новая заявка от @{update.message.from_user.username or 'пользователя'}")
        context.bot.send_media_group(chat_id=ADMIN_ID, media=media_group)
        context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=keyboard)

        update.message.reply_text("Спасибо! Твои работы отправлены на рассмотрение. Жди ответа от @razesigm ✉️")
    elif len(user_submissions[user_id]) < 3:
        update.message.reply_text(f"Фото {len(user_submissions[user_id])}/3 принято. Отправь ещё {3 - len(user_submissions[user_id])}.")
    else:
        update.message.reply_text("Ты уже отправил 3 фото. Пожалуйста, дождись ответа.")

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])
        context.bot.send_message(chat_id=user_id, text="🎉 Твои работы одобрены, спасибо! 💫")
        query.edit_message_text("✅ Работы одобрены.")
    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        context.bot.send_message(chat_id=user_id, text="❌ К сожалению, твои работы не были одобрены 😔")
        query.edit_message_text("❌ Работы не одобрены.")
    if user_id in user_submissions:
        del user_submissions[user_id]

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
