import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import DELAY, get_user_info, find_people, content_generator
from dbdeliriuminator.classdbinator import *
from cities import get_city_list
from keyboards import KEYBOARD_start, KEYBOARD_main, KEYBOARD_yes_or_no, KEYBOARD_favorites
from random import randrange
from time import sleep


def bot(user_token, public_token, db_user_name='postgres', db_password='1234', db='vkinder'):

    db = DeliriumBDinator(username=db_user_name, password=db_password, database=db)
    vk_me = vk_api.VkApi(token=user_token, api_version='5.131').get_api()
    vk_bot = vk_api.VkApi(token=public_token, api_version='5.131')
    longpoll = VkLongPoll(vk_bot)

    keyboards = {0: KEYBOARD_start,       # Позиция 0. Когда только что пришёл - кнопка СТАРТ
                 1: KEYBOARD_main,        # Позиция 1. Когда прошёл все проверки и нажал СТАРТ - кнопки: Ещё, Стоп, Добавить в избранное, Открыть избранное
                 2: KEYBOARD_yes_or_no,   # Позиция 2. Когда нажал Добавить в избранное - кнопки: Да, Нет
                 3: KEYBOARD_favorites,   # Позиция 3. Когда нажал Открыть избранное - кнопки: Удалить, В главное меню
                 4: '',                   # Позиция 4. Когда просят ввести ID для удаления из избранного
                 404: '',                 # Позиция 404. Когда нет возраста - нет кнопок
                 405: ''}                 # Позиция 405. Когда нет города - нет кнопок

    def write_msg(user_id, message='', attachment='', keyboard='', send_last=False):
        if not keyboard:
            keyboard = keyboards[db.get_position(int(user_id))]
        if send_last:
            last_send_person_info, last_send_person_photos, last_id = db.get_last_send_person(int(user_id))
            message = message + '\n' + last_send_person_info
            attachment = ','.join(last_send_person_photos)
        sleep(DELAY)
        vk_bot.method('messages.send', {'user_id': user_id,
                                        'message': message,
                                        'attachment': attachment,
                                        'keyboard': keyboard,
                                        'random_id': randrange(10 ** 7)})

    def __get_photos_args(list_of_photo):
        photos_dict = {'photo_1': None,
                       'photo_2': None,
                       'photo_3': None}
        counter = 1
        for photo in list_of_photo:
            photos_dict[f'photo_{counter}'] = photo
            counter += 1
        return photos_dict

    def send_next_person(copy_person=True):
        person = db.get_next_person(int(user_id))
        if person:
            person_id, first_name, surname, link, photos = content_generator(person, vk_me)
            if copy_person:
                db.set_last_send_person(int(user_id), int(person_id),
                                        name=first_name, surname=surname,
                                        data=link, **__get_photos_args(photos))
            write_msg(user_id, f'{first_name} {surname}\n{link}', ','.join(photos))
        else:
            db.update_user(int(user_id), position=0)
            write_msg(user_id, 'Нет анкет!')
            db.delete_find_people(int(user_id))

    def start(user_sex, user_age, user_city_title, vk_me):
        db.update_user(int(user_id), position=1)
        if not db.get_next_person(int(user_id)):
            db.add_find_people(user_id, find_people(user_sex, user_age, user_city_title, vk_me))
        send_next_person()

    def open_favorites(user_id):
        favorites = db.get_user_favorites(int(user_id))
        if favorites:
            db.update_user(int(user_id), position=3)
            write_msg(user_id, 'Ваше избранное:')
            for favorite in favorites:
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

                position = db.get_position(int(user_id))

                if position == 0 and request.lower() == "старт":

                    if not any(db.get_user(int(user_id))[-3:-1]):
                        user_sex, user_age, user_city_title = get_user_info(user_id, vk_me)
                        db.update_user(int(user_id), sex=user_sex,
                                       age=user_age, city=user_city_title)
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
                        start(user_sex=data[-4], user_age=data[-3],
                              user_city_title=data[-2], vk_me=vk_me)

                elif position == 404 and request.isdigit() and int(request) < 70:
                    db.update_user(int(user_id), age=int(request))
                    write_msg(user_id, 'Принято')
                    if db.get_user(int(user_id))[-2]:
                        data = db.get_user(int(user_id))
                        start(user_sex=data[-4], user_age=data[-3],
                              user_city_title=data[-2], vk_me=vk_me)
                    else:
                        db.update_user(int(user_id), position=405)
                        write_msg(user_id, 'Введите Ваш Город')

                elif position == 405:
                    try:
                        index = get_city_list('cities.json')[0].index(request.strip().lower().replace('-', ' '))
                        db.update_user(int(user_id), city=get_city_list('cities.json')[1][index])
                        write_msg(user_id, 'Принято')
                        if db.get_user(int(user_id))[-4]:
                            data = db.get_user(int(user_id))
                            start(user_sex=data[-4], user_age=data[-3],
                                  user_city_title=data[-2], vk_me=vk_me)
                        else:
                            db.update_user(int(user_id), position=404)
                            write_msg(user_id, 'Введите Ваш Возраст')
                    except ValueError:
                        write_msg(user_id, 'Неверный ввод! Введите Ваш город')

                elif position == 1 and request == 'Ещё':
                    send_next_person()

                elif position == 1 and request == 'Стоп':
                    db.update_user(int(user_id), position=0)
                    write_msg(user_id, 'Хорошего Вам дня!')

                elif position == 1 and request == 'Добавить в избранное':
                    db.update_user(int(user_id), position=2)
                    write_msg(user_id,
                              'Вы уверены, что хотите добавить текущего пользователя в избранное?',
                              send_last=True)

                elif position == 2 and request == 'Да':
                    last_send_person_info, last_send_person_photos, last_id = db.get_last_send_person(int(user_id))
                    if db.is_favorites(last_id):
                        db.update_user(int(user_id), position=1)
                        write_msg(user_id,
                                  'Ошибка! Данный пользователь уже добавлен избранное\n' + last_send_person_info,
                                  ','.join(last_send_person_photos)) #БД
                    else:
                        db.add_favorites(int(user_id), last_id,
                                         name=last_send_person_info.split('\n')[0].split()[0],
                                         surname=last_send_person_info.split('\n')[0].split()[1],
                                         data=last_send_person_info.split('\n')[1],
                                         **__get_photos_args(last_send_person_photos))
                        db.update_user(int(user_id), position=1)
                        write_msg(user_id, 'Добавлено!', send_last=True)

                elif position == 2 and request == 'Нет':
                    db.update_user(int(user_id), position=1)
                    write_msg(user_id, 'Не добавлено!', send_last=True)

                elif position == 1 and request == 'Открыть избранное':
                    open_favorites(user_id)

                elif position == 3 and request == 'Главное меню':
                    db.update_user(int(user_id), position=1)
                    write_msg(user_id, send_last=True)

                elif position == 3 and request == 'Удалить':
                    db.update_user(int(user_id), position=4)
                    write_msg(user_id, 'Введите ID пользователя для удаления')

                elif position == 4 and request.isdigit() and db.is_user_favorites(user_id, int(request)):
                    db.delete_favorites(user_id, int(request))
                    db.update_user(int(user_id), position=3)
                    write_msg(user_id, f'Пользователь с id {request} успешно удалён')
                    open_favorites(user_id)

                else:
                    write_msg(user_id, 'Не поняла вашего ответа...')
