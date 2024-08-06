from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes,CallbackContext,CallbackQueryHandler

TOKEN = '6947402319:AAEAx0tj9I0kYPm2sPuVafUUEMSKfbwERAc'
OWNER_ID = '543664962'


user_states = {}

# Create a ReplyKeyboardMarkup with command buttons
reply_keyboard = [
    [KeyboardButton('/start'), KeyboardButton('/help')],
    [KeyboardButton('/miniapp'), KeyboardButton('/feedback')]
]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Open Mini App", url="https://t.me/DpsNet_bot/DPS_NET")]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Привет! Я ваш бот для Mini Apps.\n\nДоступные команды:',
        reply_markup=inline_markup
    )
    # Send the reply keyboard with commands
    await update.message.reply_text(
        'Вы можете использовать следующие команды:',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Доступные команды:\n'
        '/start - Начать работу с ботом\n'
        '/help - Получить помощь\n'
        '/miniapp - Информация о Mini Apps\n'
        '/feedback - Отправить отзыв владельцу бота',
        reply_markup=reply_markup
    )

async def miniapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Здесь будет информация о Mini Apps.', reply_markup=reply_markup)

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Mark this user as ready to send feedback
    user_states[user_id] = 'awaiting_feedback'
    await update.message.reply_text('Пожалуйста, введите ваше сообщение для отправки владельцу бота.', reply_markup=reply_markup)

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # Check if the user is in the feedback state
    if user_states.get(user_id) == 'awaiting_feedback':
        user_message = update.message.text
        # Send the message to the bot owner
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"Сообщение от пользователя {update.message.from_user.username or update.message.from_user.id}:\n\n{user_message}"
        )
        # Confirm receipt to the user
        await update.message.reply_text('Ваше сообщение отправлено владельцу бота.', reply_markup=reply_markup)
        # Reset user state
        user_states[user_id] = None
    else:
        await update.message.reply_text('Используйте команду /feedback чтобы отправить сообщение владельцу бота.', reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'help':
        await help_command(update, context)
    elif query.data == 'miniapp':
        await miniapp_command(update, context)
    elif query.data == 'feedback':
        await feedback_command(update, context)

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("miniapp", miniapp_command))
    app.add_handler(CommandHandler("feedback", feedback_command))
    # Use filters to catch all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Handle button clicks
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == '__main__':
    main()