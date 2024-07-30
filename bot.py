from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


TOKEN = '6947402319:AAEAx0tj9I0kYPm2sPuVafUUEMSKfbwERAc'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я ваш бот для Mini Apps.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Спросите меня о чем-нибудь или используйте команду /miniapp.')

async def miniapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Здесь будет логика для взаимодействия с Mini Apps API
    await update.message.reply_text('Здесь будет информация о Mini Apps.')

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("miniapp", miniapp_command))

    app.run_polling()

if __name__ == '__main__':
    main()
