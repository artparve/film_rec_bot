import pandas as pd

df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0' )
df_users = pd.read_csv('df_users.csv',index_col='Unnamed: 0' )

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

FILM, YEARS, LOCATION, BIO,SAMENAME = range(5)

movies_df = pd.read_csv('movies.csv')	

reply_keyboard_film = [['/cancel', 'The Gentlemen 9', 'The Tourist 7', 'Darkness 3']]

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
          context.user_data['films'] = '\n'.join(list(df_us_mov['movie_id'][df_us_mov['id_coded']==context.user_data['id'] ]))+'\n'

        
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
    note = update.message.text[-1]
    years = list(movies_df['year'][movies_df['title'] == film])
    logger.info("Film of %s: %s", user.first_name, update.message.text)
    print(f'film {update.message.text}, context.user_data: {context.user_data}')
    
    #если фильм уже был
    if film in context.user_data['films']:
      n = context.user_data['films'].find(film)+len(film)+2
      e = context.user_data['films'][n:].find(')')

      #других нет в базе - return FIL
      if len(context.user_data['films'][n:n+e].split(' ,')) >= len(years):
        update.message.reply_text(
        f"Вы уже добавляли фильм {context.user_data['films'][n-len(film)-2:n+e]}. Попробуйте добавить другой", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film)
        )
        return FILM

      #другиe есть в базе
      else:
        # print(f'years: {years}, хочу удалить {context.user_data["films"][n+len( film)+2:n+len(film)+7]}')
        for i in context.user_data['films'][n:n+e].split(' ,'):
          years.remove(i)
        context.user_data['years'] = years
        update.message.reply_text(
          f"Вы уже добавляли фильм {context.user_data['films'][n-len(film)-2:n+e+1]}", 
          reply_markup=ReplyKeyboardMarkup([['Тогда ладно'], years, ['Другой год']])
        )

    #нет в базе - return FILM
    elif len(years) < 1:
      update.message.reply_text(
        f"В моей базе, к сожалению, нет фильма {film}", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film)
      )
      return FILM

    #в базе такой один
    elif len(years) == 1:
      update.message.reply_text(
        f"Фильм {years[0]} года правильно?", 
        reply_markup = ReplyKeyboardMarkup(reply_keyboard)
      )

    #в базе таких много
    else: 
      update.message.reply_text(
        f"Уточните год, пожалуйста...", reply_markup = ReplyKeyboardMarkup([years,['Другой']])
      )

    #обработка years
    context.user_data['film'] = film
    context.user_data['note'] = note
    context.user_data['years'] = years
    return YEARS


def years(update: Update, context: CallbackContext) -> int:
    df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0')
    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')

    user = update.message.from_user
    text = update.message.text 
    id = context.user_data['id']
    film = context.user_data['film']
    note = context.user_data['note']
    years = context.user_data['years']

    logger.info("ыыыыыыыыыыыы of %s: %s", user.first_name, 'ы')
    print(f'years {update.message.text}, context.user_data: {context.user_data}')

    if text in ['Нет', 'Другой', 'Тогда ладно'] or (text.isdigit() and text not in years):
      update.message.reply_text(
          'Тогда такого фильма нет в базе( Попробуй другой фильм', 
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film)
      )

    elif 'да' in text.lower():
      #добавляем в базу
      df_us_mov.loc[len(df_us_mov)] = [id, f'{film} ({years[0]})', note]
      print(df_us_mov)
      df_us_mov.to_csv('df_us_mov.csv')
      #Добавляем в список пользователя новый фильм
      context.user_data['films'] = f'{context.user_data["films"]}{film} ({years[0]})\n'
      #говорим об этом пользователю
      update.message.reply_text(
          f'Супер, я запомнил) {film} ({years[0]})',  
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))
    
    elif text.isdigit() and text in years:
        df_us_mov.loc[len(df_us_mov)] = [id, f'{film} ({text})', note]
        #новый год в существующие скобки
        if film in context.user_data['films']:
          n = context.user_data['films'].find(film)
          e = context.user_data['films'][n:].find(')')
          context.user_data['films'] = context.user_data['films'][:e-1]+f' ,{text}'+context.user_data['films'][e:]
        #просто новый фильм 
        else:
          context.user_data['films'] = f'{context.user_data["films"]}{film} ({text})\n'
        print(df_us_mov)
        df_us_mov.to_csv('df_us_mov.csv')
        update.message.reply_text(f'Супер, я запомнил) {film} ({text})', 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))
    
    else:
      update.message.reply_text('Я не понимаю, что-то не так с форматом, попробуй еще раз!')
      return YEARS
    
    del context.user_data['film']
    del context.user_data['note']
    del context.user_data['years']
    return FILM


def skip_photo(update: Update, context: CallbackContext) -> int:
    print(f'skip_photo {update.message.text}')
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Окей, и что дальше?'
    )

    return LOCATION

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
            YEARS: [MessageHandler(Filters.regex('^\s|\w|\d*$'), years),
                    CommandHandler('skip', skip_photo),
                    CommandHandler('cancel', cancel)],
            LOCATION: [MessageHandler(Filters.regex('^\s|\w|\d*$'), skip_photo),
                       CommandHandler('skip', skip_location),
                       CommandHandler('cancel', cancel)],
            SAMENAME: [MessageHandler(Filters.regex('^\s|\w|\d*$'), film),
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