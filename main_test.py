import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if user:
        name = user.first_name
    else:
        name = 'Анонимус'
    update.message.reply_text('Hi, {}!'.format(name))
    update.message.reply_text('Меня зовут ПокаБесполезныйБот, и я пока умею только здороваться')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Это я пока не умею')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

def action(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Здесь будет экшн')
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)
    
def hello(update, context):
    global option
    option = update.message.text
    update.message.reply_text('Привет!')
    

def main():
    """Start the bot."""
    print('Start')
    updater = Updater("1247859285:AAHSu4GPAOFVrpA8ZB_dJUnibLuE3UbSio4", use_context=True)
        # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("action", action))
    dp.add_handler(CommandHandler("echo", echo))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, hello))
  

    # on noncommand i.e message - echo the message on Telegram
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()
    print('Finish')

option = ""

if __name__ == '__main__':
    main()