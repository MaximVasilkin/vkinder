import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import *
from string import digits, punctuation, whitespace
from dbdeliriuminator import  *
from cities import get_city_list

vk_me = authorize('tokens.ini', my_token=True)
vk_bot = authorize('tokens.ini', bot_token=True)
longpoll = VkLongPoll(vk_bot)


user_info = {}       #  {'user_vk_id': {'user_position': None,
                     #                  'user_sex': None,
                     #                  'user_age': None,
                     #                  'user_city_title': None}}

persons = {}         # Тут подобранные пользователю люди в формате: {'user_vk_id': generator_of_people}

last_message = ''    # Тут последнее отправленное сообщение, ЕСЛИ параметр copy_message=True при вызове функции write_msg
last_person = []     # Тут последняя отправленная анкета, ЕСЛИ параметр copy_person=True при вызове функции write_msg

keyboards = {0: KEYBOARD_start,       # Позиция 0. Когда только что пришёл - кнопка СТАРТ
             1: KEYBOARD_main,        # Позиция 1. Когда прошёл все проверки и нажал СТАРТ - кнопки: Ещё, Стоп, Добавить в избранное, Открыть избранное
             2: KEYBOARD_yes_or_no,   # Позиция 2. Когда нажал Добавить в избранное - кнопки: Да, Нет
             3: KEYBOARD_favorites,   # Позиция 3. Когда нажал Открыть избранное - кнопки: Удалить, В главное меню
             404: '',                 # Позиция 404. Когда нет возраста - нет кнопок
             405: ''}                 # Позиция 405. Когда нет города - нет кнопок


def write_msg(user_id, message='', attachment='', person_id=None, keyboard='', copy_message=False, copy_person=False):
    global last_message, last_person, user_info
    if not keyboard:
        keyboard = keyboards[user_info[user_id]['user_position']]
    sleep(DELAY)
    vk_bot.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'attachment': attachment,
                                    'keyboard': keyboard,
                                    'random_id': randrange(10 ** 7)})
    if copy_message:
        last_message = message
    elif copy_person:
        last_person = (message, attachment, person_id)



def send_next_person():
    try:
        write_msg(user_id, *next(persons[user_id]), copy_person=True)
    except StopIteration:
        write_msg(user_id, 'Нет анкет!')


def start(user_sex, user_age, user_city_title, vk_me):
    user_info[user_id]['user_position'] = 1
    persons[user_id] = content_generator(find_people(user_sex, user_age, user_city_title, vk_me), vk_me)
    send_next_person()



for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            user_id = str(event.user_id)
            request = event.text

            user_info.setdefault(user_id, {'user_position': 0})

            if user_info[user_id]['user_position'] == 0 and request.lower() == "старт":
                user_sex, user_age, user_city_title = get_user_info(user_id, vk_me)
                user_info[user_id] = {'user_position': 0,
                                      'user_sex': user_sex,
                                      'user_age': user_age,
                                      'user_city_title': user_city_title}

                if not get_user(int(user_id)):  #БД
                    add_user(int(user_id))      #БД

                if not user_age:
                    user_info[user_id]['user_position'] = 404
                    write_msg(user_id, 'Введите Ваш возраст')
                elif not user_city_title:
                    user_info[user_id]['user_position'] = 405
                    write_msg(user_id, 'Введите Ваш Город')
                else:
                    start(user_sex, user_age, user_city_title, vk_me)



            elif user_info[user_id]['user_position'] == 404 and not request.isdigit():
                write_msg(user_id, 'Неверный ввод! Введите Ваш возраст')
            elif user_info[user_id]['user_position'] == 404 and request.isdigit():
                user_info[user_id]['user_age'] = int(request)
                write_msg(user_id, 'Принято')
                if user_info[user_id]['user_city_title']:
                    start(*list(user_info[user_id].values())[1:], vk_me)
                else:
                    user_info[user_id]['user_position'] = 405
                    write_msg(user_id, 'Введите Ваш Город')


            elif user_info[user_id]['user_position'] == 405 and any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]) :
                write_msg(user_id, 'Неверный ввод! Введите Ваш город')
            elif user_info[user_id]['user_position'] == 405 and not any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]) and request.strip() not in get_city_list('cities.json'):
                write_msg(user_id, 'Отсутствует в списке городов')
            elif user_info[user_id]['user_position'] == 405 and not any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]) and request.strip() in get_city_list('cities.json'):
                user_info[user_id]['user_city_title'] = request.strip()
                write_msg(user_id, 'Принято')
                if user_info[user_id]['user_age']:
                    start(*list(user_info[user_id].values())[1:], vk_me)
                else:
                    user_info[user_id]['user_position'] = 404
                    write_msg(user_id, 'Введите Ваш Возраст')



            elif user_info[user_id]['user_position'] == 1 and request == 'Ещё':
                send_next_person()

            elif user_info[user_id]['user_position'] == 1 and request == 'Стоп':
                user_info[user_id]['user_position'] = 0
                write_msg(user_id, 'Хорошего Вам дня!')

            elif user_info[user_id]['user_position'] == 1 and request == 'Добавить в избранное':
                user_info[user_id]['user_position'] = 2
                write_msg(user_id, 'Вы уверены, что хотите добавить текущего пользователя в избранное?\n' + last_person[0], last_person[1])

            elif user_info[user_id]['user_position'] == 2 and request == 'Да':

                add_favorites(int(user_id), last_person[2]) #БД

                user_info[user_id]['user_position'] = 1
                write_msg(user_id, 'Добавлено!\n' + last_person[0], last_person[1])

            elif user_info[user_id]['user_position'] == 2 and request == 'Нет':
                user_info[user_id]['user_position'] = 1
                write_msg(user_id, 'Не добавлено!\n' + last_person[0], last_person[1])

            elif user_info[user_id]['user_position'] == 1 and request == 'Открыть избранное':
                user_info[user_id]['user_position'] = 3

                for favorite in get_favorites(int(user_id)): #БД

                    write_msg(user_id, favorite[0])


            elif user_info[user_id]['user_position'] == 3 and request == 'Главное меню':
                user_info[user_id]['user_position'] = 1
                write_msg(user_id, last_person[0], last_person[1])

            else:
                write_msg(user_id, 'Не поняла вашего ответа...')