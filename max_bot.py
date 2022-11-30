import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import *
from string import digits, punctuation, whitespace
#from dbdeliriuminator import  *
from newdb.dbclass import *


db = DeliriumBDinator()

vk_me = authorize('tokens.ini', my_token=True)
vk_bot = authorize('tokens.ini', bot_token=True)
longpoll = VkLongPoll(vk_bot)


user_info = {}       #  {'user_vk_id': {'user_position': None,
                     #                  'user_sex': None,
                     #                  'user_age': None,
                     #                  'user_city_title': None}}

persons = {}         # Тут подобранные пользователю люди в формате: {'user_vk_id': generator_of_people}
last_person = []     # Тут последняя отправленная анкета, ЕСЛИ параметр copy_person=True при вызове функции write_msg

keyboards = {0: KEYBOARD_start,       # Позиция 0. Когда только что пришёл - кнопка СТАРТ
             1: KEYBOARD_main,        # Позиция 1. Когда прошёл все проверки и нажал СТАРТ - кнопки: Ещё, Стоп, Добавить в избранное, Открыть избранное
             2: KEYBOARD_yes_or_no,   # Позиция 2. Когда нажал Добавить в избранное - кнопки: Да, Нет
             3: KEYBOARD_favorites,   # Позиция 3. Когда нажал Открыть избранное - кнопки: Удалить, В главное меню
             4: '',                   # Позиция 4. Когда просят ввести ID для удаления из избранного
             404: '',                 # Позиция 404. Когда нет возраста - нет кнопок
             405: ''}                 # Позиция 405. Когда нет города - нет кнопок


def write_msg(user_id, message='', attachment='', person_id=None, keyboard='', copy_person=False):
    global last_person, user_info
    if not keyboard:
        keyboard = keyboards[db.get_user(int(user_id))[1]]
    sleep(DELAY)
    vk_bot.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'attachment': attachment,
                                    'keyboard': keyboard,
                                    'random_id': randrange(10 ** 7)})
    if copy_person:
        last_person = (message, attachment, person_id)


def send_next_person():
    try:
        write_msg(user_id, *next(persons[user_id]), copy_person=True)
    except StopIteration:
        db.update_user(int(user_id), position=0)
        write_msg(user_id, 'Нет анкет!')


def start(user_sex, user_age, user_city_title, vk_me):
    db.update_user(int(user_id), position=1)
    persons[user_id] = content_generator(find_people(user_sex, user_age, user_city_title, vk_me), vk_me)
    send_next_person()


def open_favorites(user_id):
    favorites = db.get_user_favorites(int(user_id))
    if favorites:  # БД
        db.update_user(int(user_id), position=3)
        for favorite in favorites:  # БД
            message = f'{favorite[2]} {favorite[3]}\n{favorite[-3]}'
            attachment = ','.join([photo for photo in favorite[8:11] if photo])
            write_msg(user_id, message, attachment)
    else:
        db.update_user(int(user_id), position=1)
        write_msg(user_id, 'Ваше избранное пусто')


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            user_id = str(event.user_id)
            request = event.text

            if not db.is_user(int(user_id)):
                db.add_user(int(user_id), position=0)


            #user_info.setdefault(user_id, {'user_position': 0})

            if db.get_user(int(user_id))[1] == 0 and request.lower() == "старт":



                if not any(db.get_user(int(user_id))[-3:-1]):  #БД
                    user_sex, user_age, user_city_title = get_user_info(user_id, vk_me)
                    db.update_user(int(user_id), sex=user_sex, age=user_age, city=user_city_title)
                    if not user_age:
                        db.update_user(int(user_id), position=404)
                        write_msg(user_id, 'Введите Ваш возраст')
                    elif not user_city_title:
                        db.update_user(int(user_id), position=405)
                        write_msg(user_id, 'Введите Ваш Город')
                    else:
                        start(user_sex, user_age, user_city_title, vk_me)
                else:
                    data = db.get_user(int(user_id))
                    start(user_sex=data[-4], user_age=data[-3], user_city_title=data[-2], vk_me=vk_me)


                # user_info[user_id] = {'user_position': 0,
                #                       'user_sex': user_sex,
                #                       'user_age': user_age,
                #                       'user_city_title': user_city_title}


            elif db.get_user(int(user_id))[1] == 404 and not request.isdigit():
                write_msg(user_id, 'Неверный ввод! Введите Ваш возраст')
            elif db.get_user(int(user_id))[1] == 404 and request.isdigit():
                db.update_user(int(user_id), age=int(request))
                #user_info[user_id]['user_age'] = int(request)
                write_msg(user_id, 'Принято')
                if db.get_user(int(user_id))[-2]:
                    data = db.get_user(int(user_id))
                    start(user_sex=data[-4], user_age=data[-3], user_city_title=data[-2], vk_me=vk_me)
                else:
                    db.update_user(int(user_id), position=405)
                    write_msg(user_id, 'Введите Ваш Город')


            elif db.get_user(int(user_id))[1] == 405 and any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]):
                write_msg(user_id, 'Неверный ввод! Введите Ваш город')
            elif db.get_user(int(user_id))[1] == 405 and not any([item in request for item in [*digits, *punctuation.replace('-', ''), *whitespace[1:]]]):
                #user_info[user_id]['user_city_title'] = request.strip()
                db.update_user(int(user_id), city=request.strip())
                write_msg(user_id, 'Принято')
                if db.get_user(int(user_id))[-4]:
                    #start(*list(user_info[user_id].values())[1:], vk_me)
                    data = db.get_user(int(user_id))
                    start(user_sex=data[-4], user_age=data[-3], user_city_title=data[-2], vk_me=vk_me)
                else:
                    db.update_user(int(user_id), position=404)
                    write_msg(user_id, 'Введите Ваш Возраст')



            elif db.get_user(int(user_id))[1] == 1 and request == 'Ещё':
                send_next_person()

            elif db.get_user(int(user_id))[1] == 1 and request == 'Стоп':
                db.update_user(int(user_id), position=0)
                write_msg(user_id, 'Хорошего Вам дня!')

            elif db.get_user(int(user_id))[1] == 1 and request == 'Добавить в избранное':
                db.update_user(int(user_id), position=2)
                write_msg(user_id, 'Вы уверены, что хотите добавить текущего пользователя в избранное?\n' + last_person[0], last_person[1])

            elif db.get_user(int(user_id))[1] == 2 and request == 'Да':
                if db.is_favorites(last_person[2]):
                    db.update_user(int(user_id), position=1)
                    write_msg(user_id, 'Ошибка! Данный пользователь уже добавлен избранное\n' + last_person[0], last_person[1]) #БД
                else:
                    photos = {'photo_1': None,
                              'photo_2': None,
                              'photo_3': None}
                    counter = 1
                    for photo in last_person[1].split(','):
                        photos[f'photo_{counter}'] = photo
                        counter += 1
                    counter = 0


                    db.add_favorites(int(user_id), last_person[2], name=last_person[0].split('\n')[0].split()[0], surname=last_person[0].split('\n')[0].split()[1], data=last_person[0].split('\n')[1], **photos) #БД !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WORK
                    db.update_user(int(user_id), position=1)
                    write_msg(user_id, 'Добавлено!\n' + last_person[0], last_person[1])

            elif db.get_user(int(user_id))[1] == 2 and request == 'Нет':
                db.update_user(int(user_id), position=1)
                write_msg(user_id, 'Не добавлено!\n' + last_person[0], last_person[1])

            elif db.get_user(int(user_id))[1] == 1 and request == 'Открыть избранное':
                open_favorites(user_id)

            elif db.get_user(int(user_id))[1] == 3 and request == 'Главное меню':
                db.update_user(int(user_id), position=1)
                write_msg(user_id, last_person[0], last_person[1])

            elif db.get_user(int(user_id))[1] == 3 and request == 'Удалить':
                db.update_user(int(user_id), position=4)
                write_msg(user_id, 'Введите ID пользователя для удаления')

            elif db.get_user(int(user_id))[1] == 4 and request.isdigit() and db.is_user_favorites(user_id, request):
                db.delete_favorites(user_id, request)
                db.update_user(int(user_id), position=3)
                write_msg(user_id, f'Пользователь с id {request} успешно удалён')
                open_favorites(user_id)

            else:
                write_msg(user_id, 'Не поняла вашего ответа...')