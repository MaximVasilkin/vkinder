import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import *
from string import digits, punctuation, whitespace


vk_me = authorize('tokens.ini', my_token=True)
vk_bot = authorize('tokens.ini', bot_token=True)
longpoll = VkLongPoll(vk_bot)


def write_msg(user_id, message, attachment='', keyboard=''):
    global last_person, last_keyboard
    sleep(DELAY)
    vk_bot.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'attachment': attachment,
                                    'keyboard': keyboard,
                                    'random_id': randrange(10 ** 7)})
    if keyboard:
        last_keyboard = keyboard
    if message and attachment:
        last_person = (message, attachment)


messages = {}
user_info = {'user_vk_id': {'user_position': None,
                            'user_sex': None,
                            'user_age': None,
                            'user_city_title': None}}
last_person = []
last_keyboard = KEYBOARD_start

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            user_id = str(event.user_id)
            request = event.text

            user_info.setdefault(user_id, {'user_position': None})

            if request.lower() == "старт":
                user_sex, user_age, user_city_title = get_user_info(user_id, vk_me)
                user_info[user_id] = {'user_position': 0,
                                      'user_sex': user_sex,
                                      'user_age': user_age,
                                      'user_city_title': user_city_title}

                if not user_age:
                    user_info[user_id]['user_position'] = 404
                    write_msg(user_id, 'Введите Ваш возраст')
                elif not user_city_title:
                    user_info[user_id]['user_position'] = 405
                    write_msg(user_id, 'Введите Ваш Город')
                else:
                    user_info[user_id]['user_position'] = 1
                    found_people = find_people(user_sex, user_age, user_city_title, vk_me)
                    messages[user_id] = create_message_for_bot(found_people, vk_me)

                    try:
                        write_msg(user_id, *next(messages[user_id]), keyboard=KEYBOARD_main)
                    except StopIteration:
                        write_msg(user_id, 'Нет анкет!', keyboard=KEYBOARD_start)


            elif user_info[user_id]['user_position'] == 404 and not request.isdigit():
                write_msg(user_id, 'Неверный ввод! Введите Ваш возраст')
            elif user_info[user_id]['user_position'] == 404 and request.isdigit():
                user_info[user_id]['user_age'] = int(request)
                write_msg(user_id, 'Принято')
                if user_info[user_id]['user_city_title']:
                    user_info[user_id]['user_position'] = 1
                    found_people = find_people(*list(user_info[user_id].values())[1:], vk_me)
                    messages[user_id] = create_message_for_bot(found_people, vk_me)
                    try:
                        write_msg(user_id, *next(messages[user_id]), keyboard=KEYBOARD_main)
                    except StopIteration:
                        write_msg(user_id, 'Нет анкет!', keyboard=KEYBOARD_start)
                else:
                    user_info[user_id]['user_position'] = 405
                    write_msg(user_id, 'Введите Ваш Город')


            elif user_info[user_id]['user_position'] == 405 and any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]):
                write_msg(user_id, 'Неверный ввод! Введите Ваш город')
            elif user_info[user_id]['user_position'] == 405 and not any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]):
                user_info[user_id]['user_city_title'] = request.strip()
                write_msg(user_id, 'Принято')
                if user_info[user_id]['user_age']:
                    user_info[user_id]['user_position'] = 1
                    found_people = find_people(*list(user_info[user_id].values())[1:], vk_me)
                    messages[user_id] = create_message_for_bot(found_people, vk_me)
                    try:
                        write_msg(user_id, *next(messages[user_id]), keyboard=KEYBOARD_main)
                    except StopIteration:
                        write_msg(user_id, 'Нет анкет!', keyboard=KEYBOARD_start)
                else:
                    user_info[user_id]['user_position'] = 404
                    write_msg(user_id, 'Введите Ваш Возраст')



            elif user_info[user_id]['user_position'] == 1 and request == 'Ещё':
                try:
                    write_msg(user_id, *next(messages[user_id]), keyboard=KEYBOARD_main)
                except StopIteration:
                    write_msg(user_id, 'Нет анкет!', keyboard=KEYBOARD_start)
            elif user_info[user_id]['user_position'] == 1 and request == 'Стоп':
                write_msg(user_id, 'Хорошего Вам дня!', keyboard=KEYBOARD_start)
            elif user_info[user_id]['user_position'] == 1 and request == 'Добавить в избранное':
                write_msg(user_id, 'Тут логика по добавлению. Вы уверены, что хотите добавить текущего пользователя в избранное?\n' + last_person[0], last_person[1], keyboard=KEYBOARD_yes_or_no)
            elif user_info[user_id]['user_position'] == 1 and request == 'Открыть избранное':
                user_info[user_id]['user_position'] = 2
                write_msg(user_id, 'Тут список избранного из БД', keyboard=KEYBOARD_favorites)
            elif user_info[user_id]['user_position'] == 2 and request == 'Главное меню':
                user_info[user_id]['user_position'] = 1
                write_msg(user_id, *last_person, keyboard=KEYBOARD_main)
            else:
                write_msg(event.user_id, 'Не поняла вашего ответа...', keyboard=last_keyboard)