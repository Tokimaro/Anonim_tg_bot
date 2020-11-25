import telebot
from telebot import types
from db import check_user
from db import reg_db
from db import delete_user
from db import get_info
from db import select_free
from db import add_user
from db import check_status
from db import add_second_user
from db import check_companion
from db import check_open
from db import close_chat
from db import edit_db
import time

bot = telebot.TeleBot('1458248555:AAF_onnTChilq1tMKeq1OtuvLRzwvqT7z9c')


class User:  # Класс для собирания данных и добавления в бд, пользователей
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = None
        self.age = None
        self.sex = None
        self.change = None


user_dict = {}  # Словарь из пользователей


@bot.message_handler(commands=['start'])
def welcome(
        message):  # Стартовое меня, если вы не зарегистрированы, нгачнётся регистрация, иначе у вас будет выбор между действиями
    if check_user(user_id=message.from_user.id)[0]:
        mark = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        mark.add('Начать поиск', 'Посмотреть профиль', 'Удалить профиль')
        bot.send_message(message.from_user.id, "Что дальше? ", reply_markup=mark)
        bot.register_next_step_handler(message, search_prof)
    else:
        bot.send_message(message.from_user.id, "Пользоватерь не зарегестрирован, начало регистрации")
        bot.send_message(message.from_user.id, "Введите ваше имя:")
        bot.register_next_step_handler(message, reg_name)


def reg_name(message):  # Регистрация имени
    if message.text != '':
        user = User(message.from_user.id)
        user_dict[message.from_user.id] = user
        user.name = message.text
        bot.send_message(message.from_user.id, "Каков твой возраст?:")
        bot.register_next_step_handler(message, reg_age)

    else:
        bot.send_message(message.from_user.id, "Введите ваше имя:")
        bot.register_next_step_handler(message, reg_name)


def reg_age(message):  # Регистрация возраста
    age = message.text
    if not age.isdigit():
        msg = bot.reply_to(message, 'Это должно быть число')
        bot.register_next_step_handler(msg, reg_age)
        return
    user = user_dict[message.from_user.id]
    user.age = age
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Мужчина', 'Женщина')
    bot.send_message(message.from_user.id, 'Каков ваш пол?', reply_markup=markup)
    bot.register_next_step_handler(message, reg_sex)


def reg_sex(message):  # Регистрация Пола
    sex = message.text
    user = user_dict[message.from_user.id]
    if (sex == u'Мужчина') or (sex == u'Женщина'):
        user.sex = sex
        mark = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        mark.add('Мужчин', 'Женщин', 'Всех')
        bot.send_message(message.from_user.id, 'C кем хотите пообщаться?', reply_markup=mark)
        bot.register_next_step_handler(message, reg_change)

    else:
        bot.send_message(message.from_user.id, 'Что-то пошло не так')
        bot.register_next_step_handler(message, reg_sex)


def reg_change(message):  # Регистрация выбора людей, которых они ищут, по половому признаку
    if (message.text == u'Мужчин') or (message.text == u'Женщин') or (message.text == u'Всех'):
        user = user_dict[message.from_user.id]
        user.change = message.text
        bot.send_message(message.from_user.id,
                         "Проверьте введйнные данные:\n Ваше имя: " + str(user.name) + "\n Ваш возраст: " + str(
                             user.age) + "\n Ваш пол: " + str(user.sex) + "\nВы ищите: " + str(user.change))
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        bot.send_message(message.from_user.id, "Заполнить заново: ", reply_markup=markup)
        bot.register_next_step_handler(message, reg_accept)
    else:
        bot.send_message(message.from_user.id, 'Что-то пошло не так')
        bot.register_next_step_handler(message, reg_change)


def reg_accept(message):  # Потверждение регистрации или замена старых данных на новых в бд
    if (message.text == u'Да') or (message.text == u'Нет'):
        if message.text == u'Да':
            bot.send_message(message.from_user.id, "Введите ваше имя:")
            bot.register_next_step_handler(message, reg_name)
        else:
            if not check_user(user_id=message.from_user.id)[0]:
                user = user_dict[message.from_user.id]
                reg_db(user_id=user.user_id, name=user.name, old=user.age, gender=user.sex, change=user.change)
                bot.send_message(message.from_user.id, "Вы зарегестрированы:")
            else:
                if message.from_user.id in user_dict.keys():
                    user = user_dict[message.from_user.id]
                    edit_db(user_id=user.user_id, name=user.name, old=user.age, gender=user.sex, change=user.change)
            welcome(message)


def search_prof(message):  # Отображение профиля, с возможностью пересоздать профиль и инициализация поиска партнёра
    if (message.text == u'Начать поиск') or (message.text == u'Посмотреть профиль') or (
            message.text == u'Удалить профиль'):
        if message.text == u'Начать поиск':
            search_partner(message)
        elif message.text == u'Посмотреть профиль':
            user_info = get_info(user_id=message.from_user.id)
            bot.send_message(message.from_user.id,
                             "Проверьте введённые данные:\nВаше имя: " + str(user_info[2]) + "\nВаш возраст: " + str(
                                 user_info[3]) + "\nВаш пол: " + str(user_info[4]) + "\nВы ищите: " + str(user_info[5]))
            mark = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            mark.add('Да', 'Нет')
            bot.send_message(message.from_user.id, 'Заполнить заного', reply_markup=mark)
            bot.register_next_step_handler(message, reg_accept)
        else:
            delete_user(user_id=message.from_user.id)
            bot.send_message(message.from_user.id, 'Профиль удалён')
            welcome(message)
    else:
        bot.send_message(message.from_user.id, 'Что-то пошло не так')
        bot.register_next_step_handler(message, search_prof)


def search_partner(message):  # Поиск партнёра, если парнёр найден, отоюражает данные о нём и начинается чатинг
    is_open = check_open(first_id=message.from_user.id)
    if is_open[0][0]:
        bot.register_next_step_handler(message, chat)

    else:
        select = select_free()
        success = False
        if not select:
            add_user(first_id=message.from_user.id)
        else:
            for sel in select:

                if not check_status(first_id=message.from_user.id, second_id=sel[0]) or message.from_user.id == sel[0]:
                    continue

                else:
                    add_second_user(first_id=sel[0], second_id=message.from_user.id)
                    bot.send_message(message.from_user.id, 'Мы нашли вам собеседника')
                    user_info = get_info(user_id=sel[0])
                    bot.send_message(message.from_user.id,
                                     "Имя собеседника: " + str(user_info[2]) + "\nВозраст собеседника: " + str(
                                         user_info[3]) + "\nПол собеседника: " + str(user_info[4]))
                    bot.send_message(sel[0], 'Мы нашли вам собеседника')
                    user_info = get_info(user_id=message.from_user.id)
                    bot.send_message(sel[0],
                                     "Имя собеседника: " + str(user_info[2]) + "\nВозраст собеседника: " + str(
                                         user_info[3]) + "\nПол собеседника: " + str(user_info[4]))
                    success = True
                    break
        if not success:
            time.sleep(2)
            search_partner(message)
        else:
            bot.register_next_step_handler(message, chat)


def chat(message):  # реализация чата, если полльзователь напишет "/exit" и разрывает соединение
    if message.text == "/exit":
        companion = check_companion(first_id=message.from_user.id)
        bot.send_message(companion, "Ваш собеседник вышел. Напишите что-либо для продолжения работы")
        close_chat(first_id=message.from_user.id)
        welcome(message)
        return
    elif not check_open(first_id=message.from_user.id)[0][0]:
        welcome(message)
        return
    companion = check_companion(first_id=message.from_user.id)
    bot.send_message(companion, message.text)
    bot.register_next_step_handler(message, chat)


bot.polling()
