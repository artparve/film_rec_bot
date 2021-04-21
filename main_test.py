from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
    update.message.reply_text('My name is banana-ml bot. I can make your photos look like \
                              the famous pictures! Please, choose the option: \n \
                              - "1" Universe style; \n \
                              - "2" Mondrian style; \n \
                              - "3" "Starry night" style;\n\
                              - "4" Matiss style; \n \
                              - "5" Simpsons style; \n\
                              - "6" Renuar style')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def action(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Здесь будет экшн')
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)
    
def get_style(update, context):
    global option
    option = update.message.text
    update.message.reply_text('Good! Now input coef')
def get_coef(update, context):
    global coef
    coef = update.message.number
    update.message.reply_text('Good! Now send me a pic :)')
    
def get_photo(update, context):
    """Echo the user message."""
    user = update.message.from_user
    # get photo file
    photo_file = update.message.photo[-1].get_file()
    # save photo
    photo_file.download('user_photo.jpg')
    update.message.reply_text('Nice! Got your photo, styling...')
    


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

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, get_style))
    dp.add_handler(MessageHandler(Filters.text, get_coef))
    dp.add_handler(MessageHandler(Filters.photo, get_photo))

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