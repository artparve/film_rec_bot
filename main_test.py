import telebot
bot = telebot.TeleBot('1086758705:AAGsQ7j7vl9Q_25HI7Aiz0zMNyDsShcbyPw')

operation = telebot.types.ReplyKeyboardMarkup(True, True)
operation.row('*', '/')
operation.row('+', '-')
operations = ['*', '/', '+', '-']

simple_text = telebot.types.ReplyKeyboardMarkup(True, True)
simple_text.row('Калькулятор')
user_op = ['', '']

@bot.message_handler(commands=['start'])
def start_message(message):
  print(f'{message.chat.first_name} : {message.text}')
  bot.send_message(message.chat.id, "Привет!")
  print('Bot : Привет!')

@bot.message_handler(commands=['help'])
def help_message(message):
  print(f'{message.chat.first_name} : {message.text}')
  bot.send_message(message.chat.id, f"{message.chat.first_name}, Ничем не могу помочь!")
  print(f'Bot : {message.chat.first_name}, Ничем не могу помочь!')

@bot.message_handler(content_types=['text'])
def text(message):
  print(f'{message.chat.first_name} : {message.text}')
  if message.text != 'Калькулятор':
    bot.send_message(message.chat.id, 'Я кроме калькулятора ничего не умею.... Напиши "Калькулятор"', reply_markup = simple_text)
    print(f'Bot : ты не прав')
  else:
    user_op.clear
    m = bot.reply_to(message, 'Введите первое число')
    bot.register_next_step_handler(m, oper)    
    print(f'Bot : Введите первое число')

def oper(message):
  print(f'{message.chat.first_name} : {message.text}')
  try: 
    user_op[0] = int(message.text)
    op = bot.reply_to(message, 'Введите операцию', reply_markup = operation)
    bot.register_next_step_handler(op, input_sec)
    print(f'Bot : Введите операцию')
  except ValueError:
    i1  = bot.reply_to(message, 'Это не число. Попробуйте ввести число!')
    bot.register_next_step_handler(i1, oper)
    print(f'Bot : ты не прав')
def input_sec(message):
  print(f'{message.chat.first_name} : {message.text}')
  if message.text in operations:
    user_op[1] = message.text
    m = bot.reply_to(message, 'Введите второе число')
    bot.register_next_step_handler(m, solve)
    print(f'Bot : Введите второе число')
  else:
    m = bot.reply_to(message, "Я такое не умею. Попробуйте выбрать один из предложеных вариантов")
    bot.register_next_step_handler(m, input_sec)
    print(f'Bot : ты не прав')

def solve(message):
  print(f'{message.chat.first_name} : {message.text}')
  try: 
    i2 = int(message.text)
    if user_op[1] == '+':
      bot.send_message(message.chat.id, user_op[0]+i2)
      print(f'Bot : {user_op[0]+i2}')
    elif user_op[1] == '-':
      bot.send_message(message.chat.id, user_op[0] - i2)
      print(f'Bot : {user_op[0]-i2}')
    elif user_op[1] == '*':
      bot.send_message(message.chat.id, user_op[0]*i2)
      print(f'Bot : {user_op[0]*i2}')
    else:
      if i2 == 0:
        bot.send_message(message.chat.id, 'На ноль делить нельзя.')
        print(f'Bot : На ноль делить нельзя.')
      else:
        bot.send_message(message.chat.id, user_op[0]/i2)
        print(f'Bot : {user_op[0]/i2}')
  except ValueError:
    i1  = bot.reply_to(message, 'Это не число. Попробуйте ввести число!')
    bot.register_next_step_handler(i1, solve)
    print(f'Bot : ты не прав')

  
bot.polling()
