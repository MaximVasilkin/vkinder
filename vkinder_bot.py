import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from get_people import get_user_info, find_people, content_generator
from cities import get_city_list
from menu import Command, Position
from random import randrange
from time import sleep, time
from db.classdbinator import DataBaseInator
from requests.exceptions import ReadTimeout
from socket import timeout
from urllib3.exceptions import ReadTimeoutError


def bot(user_token, public_token, db_user_name='postgres', db_password='1234', db='vkinder', memory_days=0):

    db = DataBaseInator(username=db_user_name, password=db_password, database=db)
    db.connect()
    db.create_tables()

    vk_me = vk_api.VkApi(token=user_token, api_version='5.131').get_api()
    vk_bot = vk_api.VkApi(token=public_token, api_version='5.131')
    longpoll = VkLongPoll(vk_bot)

    def write_msg(user_id, message='', attachment='', keyboard='', send_last=False):
        if not keyboard:
            keyboard = Position.get_keyboard_from_position(db.get_position(user_id))
        if send_last:
            last_send_person_info, last_send_person_photos, last_id = db.get_last_send_person(user_id)
            message = message + '\n' + last_send_person_info
            attachment = ','.join(last_send_person_photos)
        sleep(0.06)
        vk_bot.method('messages.send', {'user_id': str(user_id),
                                        'message': message,
                                        'attachment': attachment,
                                        'keyboard': keyboard,
                                        'random_id': randrange(10 ** 7)})

    def __get_photos_args(list_of_photo):
        photos_dict = {f'photo_{number + 1}': photo for number, photo in enumerate(list_of_photo)}
        return photos_dict

    def send_next_person(copy_person=True):
        person = db.get_next_person(user_id)
        if person:
            person_id, first_name, surname, link, photos = content_generator(person, vk_me)
            if copy_person:
                db.set_last_send_person(user_id, int(person_id),
                                        name=first_name, surname=surname,
                                        data=link, **__get_photos_args(photos))
            write_msg(user_id, f'{first_name} {surname}\n{link}', ','.join(photos))
        else:
            db.delete_last_send_person(user_id)
            db.delete_find_people(user_id)
            db.update_user(user_id, position=0)
            write_msg(user_id, 'Нет анкет! Нажмите "Старт", чтобы повторить поиск')

    def start(vk_me, user_sex=None, user_age=None, user_city_title=None):
        write_msg(user_id, 'Анкеты скоро загрузятся. Пожалуйста, подождите &#128522;')
        db.update_user(user_id, position=1)
        if not any([user_age, user_city_title]):
            data = db.get_user(user_id)
            user_sex = data[-4]
            user_age = data[-3]
            user_city_title = data[-2]
        if not db.get_next_person(user_id, check=True):
            db.add_find_people(str(user_id), find_people(user_sex, user_age, user_city_title, vk_me))
        send_next_person()

    def open_favorites(user_id):
        favorites = db.get_user_favorites(user_id)
        if favorites:
            db.update_user(user_id, position=3)
            emoji = '&#10024;' * 3
            write_msg(user_id, f'{emoji} Ваше избранное {emoji}')
            for favorite in favorites:
                name = favorite[2]
                surname = favorite[3]
                link = favorite[-3]
                message = f'{name} {surname}\n{link}'
                photos = favorite[8:11]
                attachment = ','.join([photo for photo in photos if photo])
                write_msg(user_id, message, attachment)
        else:
            db.update_user(user_id, position=1)
            write_msg(user_id, 'Ваше избранное пусто')

    while True:
        if db.closed():
            db.connect()
        try:
            for event in longpoll.listen():

                if event.type == VkEventType.MESSAGE_NEW:

                    if event.to_me:
                        user_id = event.user_id
                        request = event.text

                        if not db.is_user(user_id):
                            db.add_user(user_id, position=0)

                        position = db.get_position(user_id)

                        if position == Position.INTRO and request.capitalize() == Command.START:
                            user_db_info = db.get_user(user_id)
                            date = user_db_info[2]
                            age, city = user_db_info[-3:-1]

                            if time() - date > (memory_days * 86400) if memory_days else -1:
                                db.delete_last_send_person(user_id)
                                db.delete_find_people(user_id)
                                db.update_user(user_id, age=0, city='', date=time())

                            if not any([age, city]):
                                user_sex, user_age, user_city_title = get_user_info(user_id, vk_me)
                                db.update_user(user_id, sex=user_sex,
                                               age=user_age, city=user_city_title)
                                if not user_age:
                                    db.update_user(user_id, position=404)
                                    write_msg(user_id, 'Введите Ваш возраст')
                                elif not user_city_title:
                                    db.update_user(user_id, position=405)
                                    write_msg(user_id, 'Введите Ваш Город')
                                else:
                                    start(user_sex=user_sex,
                                          user_age=user_age,
                                          user_city_title=user_city_title,
                                          vk_me=vk_me)
                            else:
                                start(vk_me)

                        elif position == Position.NEED_AGE and request.isdigit() and 10 < int(request) < 70:
                            db.update_user(user_id, age=int(request))
                            write_msg(user_id, 'Принято')
                            if db.get_user(user_id)[-2]:
                                start(vk_me)
                            else:
                                db.update_user(user_id, position=405)
                                write_msg(user_id, 'Введите Ваш Город')

                        elif position == Position.NEED_CITY:
                            try:
                                index = get_city_list('cities.json')[0].index(request.strip().lower().replace('-', ' '))
                                db.update_user(user_id, city=get_city_list('cities.json')[1][index])
                                write_msg(user_id, 'Принято')
                                if db.get_user(user_id)[-3]:
                                    start(vk_me)
                                else:
                                    db.update_user(user_id, position=404)
                                    write_msg(user_id, 'Введите Ваш Возраст')
                            except ValueError:
                                write_msg(user_id, 'Неверный ввод! Введите Ваш город')

                        elif position == Position.IN_MAIN_MENU and request == Command.NEXT_PERSON:
                            send_next_person()

                        elif position == Position.IN_MAIN_MENU and request == Command.STOP:
                            db.update_user(user_id, position=0)
                            write_msg(user_id, 'Хорошего Вам дня! &#127808;')

                        elif position == Position.IN_MAIN_MENU and request == Command.ADD_TO_FAVORITE:
                            db.update_user(user_id, position=2)
                            write_msg(user_id,
                                      '&#128142; Вы уверены, что хотите добавить текущего пользователя в избранное?',
                                      send_last=True)

                        elif position == Position.IN_ADD_FAVORITE_MENU and request == Command.YES:
                            last_send_person_info, last_send_person_photos, last_id = db.get_last_send_person(user_id)
                            if db.is_favorites(last_id):
                                db.update_user(user_id, position=1)
                                write_msg(user_id,
                                          '&#9940; Ошибка! Данный пользователь уже добавлен избранное\n' + last_send_person_info,
                                          ','.join(last_send_person_photos))
                            else:
                                db.add_favorites(user_id, last_id,
                                                 name=last_send_person_info.split('\n')[0].split()[0],
                                                 surname=last_send_person_info.split('\n')[0].split()[1],
                                                 data=last_send_person_info.split('\n')[1],
                                                 **__get_photos_args(last_send_person_photos))
                                db.update_user(user_id, position=1)
                                write_msg(user_id, '&#10004; Добавлено!', send_last=True)

                        elif position == Position.IN_ADD_FAVORITE_MENU and request == Command.NO:
                            db.update_user(user_id, position=1)
                            write_msg(user_id, '&#10060; Не добавлено!', send_last=True)

                        elif position == Position.IN_MAIN_MENU and request == Command.OPEN_FAVORITE:
                            open_favorites(user_id)

                        elif position == Position.IN_FAVORITE_MENU and request == Command.OPEN_MAIN_MENU:
                            db.update_user(user_id, position=1)
                            write_msg(user_id, send_last=True)

                        elif position == Position.IN_FAVORITE_MENU and request == Command.DELETE:
                            db.update_user(user_id, position=4)
                            write_msg(user_id, '&#128148; Введите ID пользователя для удаления')

                        elif position == Position.IN_DELETE_FAVORITE_MENU \
                                and request.isdigit() and db.is_user_favorites(user_id, request):
                            db.delete_favorites(user_id, request)
                            db.update_user(user_id, position=3)
                            write_msg(user_id, f'&#128687; Пользователь с id {request} успешно удалён')
                            open_favorites(user_id)

                        else:
                            write_msg(user_id, '&#128019; Не поняла вашего ответа...')
        except (ReadTimeout, timeout, ReadTimeoutError):
            sleep(0.03)
