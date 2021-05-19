import pandas as pd
d = {'id_coded': [], 'movie_id': [], 'mark': [] }
c = {'user_id': ['590887630'], 'id_coded': [1]}
df_us_mov = pd.DataFrame(data=d)
df_users = pd.DataFrame(data=c)
df_us_mov.to_csv('df_us_mov.csv')
# print(df_usersэ)
df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0' )
df_users.to_csv('df_users.csv')
# print(df_usersэ)
df_users = pd.read_csv('df_users.csv',index_col='Unnamed: 0' )
print(df_users)
print(len(df_users))
# df_users.loc[1] = ['123', len(df_users)+1]/
df_users

import logging
import pandas as pd
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

FILM, PHOTO, LOCATION, BIO,SAMENAME = range(5)

movies_df = pd.read_csv('/content/drive/MyDrive/проект_бот/movies.csv')
reply_keyboard_film = [['хватит', 'The Gentlemen 9', 'The Tourist 7', 'Darkness 3']]

def start(update: Update, context: CallbackContext) -> int:
    print('start')

    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')
    df_us_mov = pd.read_csv('df_us_mov.csv', index_col='Unnamed: 0')

    user = update.effective_user
    if user:
        name = user.first_name
        if user.id in df_users['user_id'].unique():
          hello = 'И снова здравствуйте'
          context.user_data['id']  = int(df_users['id_coded'][df_users['user_id']==user.id])
          context.user_data['films'] = '\n'.join(list(df_us_mov['movie_id'][df_us_mov['id_coded']==1]))+'\n'
        else:
          hello = 'Приятно познакомиться'
          context.user_data['id'] = len(df_users)+1
          context.user_data['films'] = []
          df_users.loc[len(df_users)] = [user.id, len(df_users)+1]
          df_users.to_csv('df_users.csv')
          print(df_users)

    else:
        name = 'Анонимус! Раз уж ты решил остаться анонимным, то запомнить твои предпочтения в кино я не смогу'

    update.message.reply_text(
        f'{hello}, {name}! Меня зовут ПокаБесполезныйБот, и я попробую посоветовать тебе фильмы.\
        \nНо для этого мне нужно знать твои предпочтения.\
        \nНапиши пожалуйста название фильма на английском и свою оценку для этого фильма от 0 до 9.\
        \nПример: ->The Gentlemen 9',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film),
    )
    print(user.id)

    return FILM


def film(update: Update, context: CallbackContext) -> int:
    df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0' )
    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')
    reply_keyboard = [['Да', 'Нет']]

    user = update.message.from_user
    film = update.message.text[:-2]
    years = list(movies_df['year'][movies_df['title'] == film]) 
    
    if film in context.user_data['films']:
      n = context.user_data['films'].find(film)
      update.message.reply_text(
        f"Вы уже добавляли фильм {context.user_data['films'][n:n+len(film)+7]}", 
        reply_markup=ReplyKeyboardMarkup([['Тогда ладно'],['Другой год']])
      )
      return SAMENAME
    logger.info("Film of %s: %s", user.first_name, update.message.text)
    print(f'film {update.message.text}, context.user_data: {context.user_data}')
   
    if len(years) < 1:
      update.message.reply_text(
        f"В моей базе, к сожалению, нет фильма {film}", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film)
      )
      return FILM
    
    if len(years) == 1:
      update.message.reply_text(
        f"Фильм {years[0]} года правильно?", 
        reply_markup = ReplyKeyboardMarkup(reply_keyboard)
      )
      # df_us_mov.loc[len(df_us_mov)] = [int(df_users['id_coded'][df_users['user_id']==user.id]), \
      #                                  f'{film} ({years[0]})',update.message.text[-1]]
      # print(df_us_mov)
      # df_us_mov.to_csv('df_us_mov.csv')
      context.user_data['film'] = f'{film} ({years[0]})'
      context.user_data['note'] = update.message.text[-1]

    else: #len(years) > 1
      update.message.reply_text(
        f"Уточните год, пожалуйста...", reply_markup = ReplyKeyboardMarkup([years,['Другой']])
      )
      context.user_data['film'] = film
      context.user_data['note'] = update.message.text[-1]
      # df_us_mov.loc[len(df_us_mov)] = [int(df_users['id_coded'][df_users['user_id']==user.id]), \
      #                                  film,update.message.text[-1]]
      # print(df_us_mov)
      # df_us_mov.to_csv('df_us_mov.csv')

    # print(f'context.user_data: {context.user_data}')
    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0')
    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')

    user = update.message.from_user
    text = update.message.text 
    id = context.user_data['id']
    film = context.user_data['film']
    note = context.user_data['note']

    logger.info("ыыыыыыыыыыыы of %s: %s", user.first_name, 'ы')
    print(f'photo {update.message.text}, context.user_data: {context.user_data}')

    if text == 'Нет' or text == 'Другой':
      update.message.reply_text(
          'Тогда такого фильма нет в базе( Попробуй другой фильм', 
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film)
      )

    elif 'да' in text.lower():
      df_us_mov.loc[len(df_us_mov)] = [id, film, note]
      context.user_data['films'] = f'{context.user_data["films"]}{film}\n'
      print(df_us_mov)
      df_us_mov.to_csv('df_us_mov.csv')
      update.message.reply_text(
          f'Супер, я запомнил) {film}', 
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))
    
    elif text.isdigit():
        df_us_mov.loc[len(df_us_mov)] = [id, f'{film} ({text})', note]
        context.user_data['films'] = f'{context.user_data["films"]}{film} ({text})\n'
        print(df_us_mov)
        df_us_mov.to_csv('df_us_mov.csv')
        update.message.reply_text(f'Супер, я запомнил) {film} ({text})', 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))
    
    else:
      update.message.reply_text('Я не понимаю, что-то не так с форматом, попробуй еще раз!')
      return PHOTO
    
    del context.user_data['film']
    del context.user_data['note']
    return FILM


def skip_photo(update: Update, context: CallbackContext) -> int:
    print(f'skip_photo {update.message.text}')
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Окей, и что дальше?'
    )

    return LOCATION


def samename(update: Update, context: CallbackContext) -> int:
    df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0')
    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')

    user = update.message.from_user
    text = update.message.text
    id = context.user_data['id']
    film = context.user_data['film']
    note = context.user_data['note']

    if text == 'Тогда ладно':
      update.message.reply_text(
          'Попробуй другой фильм', 
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film)
      )
      return FILM

    elif text == 'Другой год':
      df_us_mov.loc[len(df_us_mov)] = [id, film, note]
      context.user_data['films'] = f'{context.user_data["films"]}{film}\n'
      print(df_us_mov)
      df_us_mov.to_csv('df_us_mov.csv')
      update.message.reply_text(
          f'Супер, я запомнил) {film}', 
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return BIO


def what(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    print(f'what {update.message.text}')
    update.message.reply_text('Я не понимаю, что-то не так с форматом, попробуй еще раз!', 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))

    return FILM


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Закончим на сегодня, пока)', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("1247859285:AAHSu4GPAOFVrpA8ZB_dJUnibLuE3UbSio4")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FILM: [MessageHandler(Filters.regex('^\s|\w+\s\d$'), film), 
                   MessageHandler(Filters.regex('^\s|\w|\d*$'), what), 
                  #  MessageHandler(Filters.regex('^хватит$'), skip_photo),
                   CommandHandler('cancel', cancel)],
            PHOTO: [MessageHandler(Filters.regex('^\s|\w|\d*$'), photo),
                    CommandHandler('skip', skip_photo),
                    CommandHandler('cancel', cancel)],
            LOCATION: [MessageHandler(Filters.regex('^\s|\w|\d*$'), skip_photo),
                       CommandHandler('skip', skip_location),
                       CommandHandler('cancel', cancel)],
            SAMENAME: [MessageHandler(Filters.regex('^\s|\w|\d*$'), samename),
                       CommandHandler('skip', skip_location),
                       CommandHandler('cancel', cancel)]
                     # MessageHandler(Filters.regex('^\s|\w|\d*$'), what)],LOCATION: [MessageHandler(Filters.regex('^*$'), photo),
                },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()