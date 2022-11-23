import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import *


vk_me = authorize('tokens.ini', my_token=True)
vk_bot = authorize('tokens.ini', bot_token=True)
longpoll = VkLongPoll(vk_bot)


def write_msg(user_id, message):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            user_id = str(event.user_id)
            request = event.text

            if request.lower() == "старт":
                for params in create_message_for_bot(user_id, vk_me):
                    vk_bot.method('messages.send', params)
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")