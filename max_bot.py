import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import *


vk_me = authorize('tokens.ini', my_token=True)
vk_bot = authorize('tokens.ini', bot_token=True)
longpoll = VkLongPoll(vk_bot)


def write_msg(user_id, message, attachment='', keyboard=''):
    vk_bot.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'attachment': attachment,
                                    'keyboard': keyboard,
                                    'random_id': randrange(10 ** 7)})


messages = {}
user_info = {'user_vk_id': {'user_status': None,
                            'user_sex': None,
                            'user_age': None,
                            'user_city_title': None}}

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            user_id = str(event.user_id)
            request = event.text

            if request.lower() == "старт":
                user_sex, user_age, user_city_title = get_user_info(user_id, vk_me)
                user_info[user_id] = {'user_status': 0,
                                      'user_sex': user_sex,
                                      'user_age': user_age,
                                      'user_city_title': user_city_title}

                found_people = find_people(user_sex, user_age, user_city_title, vk_me)

                messages[user_id] = create_message_for_bot(found_people, vk_me)
                write_msg(user_id, *next(messages[user_id]), keyboard=KEYBOARD_main)
            elif request == 'Ещё':
                write_msg(user_id, *next(messages[user_id]), keyboard=KEYBOARD_main)
            elif request == 'Стоп':
                write_msg(user_id, 'Хорошего Вам дня!', keyboard=KEYBOARD_start)
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")