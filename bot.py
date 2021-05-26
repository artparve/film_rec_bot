import pandas as pd

df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0' )
df_users = pd.read_csv('df_users.csv',index_col='Unnamed: 0' )

import logging
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

FILM, YEARS, REC, BIO, CHECK = range(5)

movies_df = pd.read_csv('movies.csv')	

reply_keyboard_film = [['/cancel'],['The Gentlemen 9', 'The Tourist 7', 'Darkness 3']]

movies_df_rec_best = pd.read_csv('movies_df_rec_best.csv',index_col='Unnamed: 0')

import random
def recomendation(genre = 'none'):
  if genre == 'none':
    return movies_df_rec_best['film'].unique()[random.randint(0, 254)]

def start(update: Update, context: CallbackContext) -> int:
    print('start')

    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')
    df_us_mov = pd.read_csv('df_us_mov.csv', index_col='Unnamed: 0')

    user = update.effective_user
    context.user_data['check'] = [['/cancel', 'Мои фильмы'],['Добавить оценку']]
    if user:
        name = user.first_name
        #уже зареган
       if user.id in df_users['user_id'].unique():
          hello = 'И снова здравствуйте'
          if 'continued' not in context.user_data.keys():
            context.user_data['id']  = int(df_users['id_coded'][df_users['user_id']==user.id])
            context.user_data['films'] = '\n'.join(list(df_us_mov['movie_id'][df_us_mov['id_coded']==context.user_data['id']]))+'\n'
            context.user_data['n_films'] = int(len(df_us_mov[df_us_mov['id_coded']==context.user_data['id']]))
          #Можем ли советовать
          if context.user_data['n_films'] > 5 :
            context.user_data['check'] = [['/cancel', 'Мои фильмы'],['Добавить оценку'], ['Посоветуй фильм']]

        #регистрируем
        else:
          hello = 'Приятно познакомиться'
          context.user_data['id'] = len(df_users)+1
          context.user_data['films'] = ''
          df_users.loc[len(df_users)] = [user.id, len(df_users)+1]
          df_users.to_csv('df_users.csv')
          print(df_users)

    else:
        name = 'Анонимус! Раз уж ты решил остаться анонимным, то запомнить твои предпочтения в кино я не смогу'

    update.message.reply_text(
        f'{hello}, {name}! Меня зовут ПокаБесполезныйБот, и я попробую посоветовать тебе фильмы.\
        \nНо для этого мне нужно знать твои предпочтения.\
        \nНапиши пожалуйста название фильма на английском и с2вою оценку для этого фильма от 0 до 9.\
        \nПример: ->The Gentlemen 9',
        reply_markup=ReplyKeyboardMarkup(context.user_data['check']),
    )

    return CHECK


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

      #других нет в базе - return CHECK
      if len(context.user_data['films'][n:n+e].split(', ')) >= len(years):
        update.message.reply_text(
        f"Вы уже добавляли фильм {context.user_data['films'][n-len(film)-2:n+e+1]}. Попробуйте добавить другой", 
        reply_markup=ReplyKeyboardMarkup(context.user_data['check'])
        )
        return CHECK

      #другиe есть в базе
      else:
        # print(f'years: {years}, хочу удалить {context.user_data["films"][n+len( film)+2:n+len(film)+7]}')
        for i in context.user_data['films'][n:n+e].split(', '):
          print( context.user_data['films'][n:n+e].split(', '), "i: ", i)
          years.remove(i)
        context.user_data['years'] = years
        update.message.reply_text(
          f"Вы уже добавляли фильм {context.user_data['films'][n-len(film)-2:n+e+1]}", 
          reply_markup=ReplyKeyboardMarkup([['Тогда ладно'], years, ['Другой год']])
        )

    #нет в базе - return CHECK
    elif len(years) < 1:
      update.message.reply_text(
        f"В моей базе, к сожалению, нет фильма {film}", 
        reply_markup=ReplyKeyboardMarkup(context.user_data['check'])
      )
      return CHECK

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
          reply_markup=ReplyKeyboardMarkup(context.user_data['check'])
      )

    elif 'да' in text.lower():
      context.user_data['n_films'] = context.user_data['n_films']+1
      if context.user_data['n_films']> 5:
        context.user_data['check'] =  [['/cancel', 'Мои фильмы'],['Добавить оценку'], ['Посоветуй фильм']]

      #добавляем в базу
      df_us_mov.loc[len(df_us_mov)] = [id, f'{film} ({years[0]})', note]
      df_us_mov.to_csv('df_us_mov.csv')
      #Добавляем в список пользователя новый фильм
      context.user_data['films'] = f'{context.user_data["films"]}{film} ({years[0]})\n'
      #говорим об этом пользователю
      update.message.reply_text(
          f'Супер, я запомнил) {film} ({years[0]})',  
          reply_markup=ReplyKeyboardMarkup(context.user_data['check']))
    
    elif text.isdigit() and text in years:
        context.user_data['n_films'] = context.user_data['n_films']+1
        if context.user_data['n_films']> 4:
          context.user_data['check'] =  [['/cancel', 'Мои фильмы'],['Добавить оценку'], ['Посоветуй фильм']]
        df_us_mov.loc[len(df_us_mov)] = [id, f'{film} ({text})', note]
        #новый год в существующие скобки
        if film in context.user_data['films']:
          n = context.user_data['films'].find(film)+len(film)+2
          e = context.user_data['films'][n:].find(')')
          context.user_data['films'] = context.user_data['films'][:n+e]+f', {text}'+context.user_data['films'][n+e:]
        #просто новый фильм 
        else:
          context.user_data['films'] = f'{context.user_data["films"]}{film} ({text})\n'

        df_us_mov.to_csv('df_us_mov.csv')
        update.message.reply_text(f'Супер, я запомнил) {film} ({text})', 
        reply_markup=ReplyKeyboardMarkup(context.user_data['check']))
    
    else:
      update.message.reply_text('Я не понимаю, что-то не так с форматом, попробуй еще раз!')
      return YEARS
    print(df_us_mov[df_us_mov['id_coded'] == id])
    df_us_mov
    del context.user_data['film']
    del context.user_data['note']
    del context.user_data['years']
    return CHECK


def o_my(update: Update, context: CallbackContext) -> int:
    print(f'o_my {update.message.text}')
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        f'Ваши фильмы: {context.user_data["films"]}'
    )

    return CHECK


def check(update: Update, context: CallbackContext) -> int:
    df_us_mov = pd.read_csv('df_us_mov.csv',index_col='Unnamed: 0')
    df_users = pd.read_csv('df_users.csv', index_col='Unnamed: 0')

    text = update.message.text 
    user = update.effective_user

    logger.info("ыыыыыыыыыыыы of %s: %s", user.first_name, 'ы')
    print(f'check {update.message.text}, context.user_data: {context.user_data}')

    if text == 'Мои фильмы':
      update.message.reply_text(
        f'Ваши фильмы: {context.user_data["films"]}', 
        reply_markup=ReplyKeyboardMarkup(context.user_data['check']),
      )
      # update.message.reply_text(
      #     f'Сколько? У вас их {context.user_data["n_films"]} ', 
      #     reply_markup=ReplyKeyboardMarkup([['Все'], ['Последние 10'], ['Первые 10']])
      # )
      return CHECK

    elif text == 'Добавить оценку':
      update.message.reply_text(
          'Напиши пожалуйста название фильма на английском и свою оценку для этого фильма от 0 до 9.\
        \nПример: ->The Gentlemen 9',  
          reply_markup=ReplyKeyboardMarkup(reply_keyboard_film))
      return FILM
    
    elif  text == 'Посоветуй фильм':
      update.message.reply_text(f'Какой жанр?', 
        reply_markup=ReplyKeyboardMarkup([['Не важно'], ['Драма', 'Мелодрама']]))
      return REC

    
    else:
      update.message.reply_sticker('CAACAgIAAxkBAAECVbRgq7CXFs7tiP1DLrUESfzIsV_t6wACDgADwDZPEyNXFESHbtZlHwQ')
      update.message.reply_text('Я так не умею, нажми пожалуйста на одну из предложеных кнопочек!')
    
      return CHECK

def rec(update: Update, context: CallbackContext) -> int:
    print(f'rec {update.message.text}')
    user = update.message.from_user
    logger.info("User %s in rec.", user.first_name)
    # df_us_mov[df_us_mov['id_coded']==context.user_data['id']][df_us_mov['note']  ]
    update.message.reply_text(
        f'Вам может понравиться фильм {recomendation()}',
        reply_markup=ReplyKeyboardMarkup(context.user_data['check']),
      )
    return CHECK

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
        'Закончим на сегодня, пока)', reply_markup=ReplyKeyboardMarkup([['/start']])
    )
    context.user_data['continued'] = 1
    df_us_mov.to_csv('df_us_mov.csv')
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
            FILM: [CommandHandler('cancel', cancel),
                   MessageHandler(Filters.regex('^.+\s\d$'), film),
                   MessageHandler(Filters.regex('My films'), o_my), 
                   MessageHandler(Filters.regex('^\s|\w|\d*$'), what),
                #  MessageHandler(Filters.regex('^хватит$'), skip_photo),
                   ],
            YEARS: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.regex('^\s|\w|\d*$'), years),
                    ],
            REC: [CommandHandler('cancel', cancel),
                       MessageHandler(Filters.regex('^\s|\w|\d*$'), rec),
                       ],
            CHECK: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.regex('^\s|\w|\d*$'), check),
                       ]
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

    # updater = Updater("1247859285:AAHSu4GPAOFVrpA8ZB_dJUnibLuE3UbSio4")