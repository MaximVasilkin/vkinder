import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from time import sleep
from datetime import datetime
from random import randrange


def authorize(path, my_token=False, bot_token=False):
    '''
    :param path: путь к файлу с токенами, в котором первая строка - личный токен, вторая - токен сообществ
    :param my_token: какой токен использовать для ВК API
    :param bot_token: какой токен использовать для ВК API
    :return: функция возвращает object - объект VK API, к которому применяются методы от VK API.
    Например: object.photos.get(count=100, offset=0, owner_id=1)
    '''

    with open(path, 'r', encoding='utf-8') as file:
        user_token, public_token = file.readlines()
    if my_token:
        return vk_api.VkApi(token=user_token, api_version='5.131').get_api()
    elif bot_token:
        return vk_api.VkApi(token=public_token, api_version='5.131')


def get_user_info(user_name_or_id, my_token_api_object):
    '''
    :param user_name_or_id: id или имя пользователя, например: 1 или paveldurov
    :param my_token_api_object: объект, возвращенный от функции authorize(path, my_token=True)
    :return: возвращает кортеж данных о пользователе: возраст, город, пол
    '''
    sleep(DELAY)
    user_info = my_token_api_object.users.get(**{'user_ids': user_name_or_id,
                                                 'fields': 'bdate, city, sex'})[0]
    user_birthday = user_info.get('bdate', None) # str
    try:
        birthday = datetime.strptime(user_birthday, "%d.%m.%Y")
        user_age = int(((datetime.today()-birthday).days)/365)
    except TypeError:
        user_age = None
    user_city_title = user_info.get('city', {}).get('title', None) # str
    user_sex = user_info['sex']  # int: 1 - женщина, 2 - мужчина
    return bool(user_sex - 1), user_age, user_city_title


def find_people(user_sex, user_age, user_city_title, my_token_api_object):
    '''
    :param user_sex: инфо, возвращённое функцией get_user_info
    :param user_age: инфо, возвращённое функцией get_user_info
    :param user_city_title: инфо, возвращённое функцией get_user_info
    :param my_token_api_object: объект, возвращенный от функции authorize(path, my_token=True)
    :return: список найденных людей
    '''
    sleep(DELAY)
    response = my_token_api_object.users.search(**{'sort': '0',
                                                    'count': '1000',
                                                    'hometown': user_city_title,
                                                    'sex': 1 if user_sex else 2,
                                                    'status': 6,                      # семейное положение, 0 - ВСЁ, 6 — в активном поиске
                                                    'age_from': str(user_age - 3),
                                                    'age_to': str(user_age + 3),     # ищем анкеты +-3 года от возраста пользователя
                                                    'has_photo': '1'})             # строго с фото
    people = response['items']  # тут список найденных людей
    return people


def content_generator(list_of_people, my_token_api_object):
    '''
    :param list_of_people: список найденных людей для знакомства. Функция find_people
    :param my_token_api_object: объект апи, возвращаемый функцией authorize
    :return: возвращает генератор ПАРАМЕТРОВ сообщений. Параметры для ВК метода message.send, это для бота
    '''
    for person in list_of_people:
        if not person['is_closed']:  # closed - закрытый профиль, фотки у такого не собрать
            person_name = f'{person["first_name"]} {person["last_name"]}'
            person_id = person['id']
            person_link = f'https://vk.com/id{person_id}'
            message = f'{person_name}\n{person_link}'
            sleep(DELAY)
            avatars = my_token_api_object.photos.get(**{'owner_id': person_id,
                                                         'album_id': 'profile',
                                                         'rev': '1',            #  берём самые свежие фото
                                                         'extended': '1',
                                                         'count': '1000'})['items']
            avatars.sort(key=lambda x: x['likes']['count'])
            avatars = avatars[-3:]
            three_most_liked = [f'photo{photo["owner_id"]}_{photo["id"]}' for photo in avatars] # [max(photo['sizes'], key=lambda x: x['width'])['url'] for photo in avatars]
            attachment = ','.join(three_most_liked)
            yield message, attachment, int(person_id)


def create_keyboard(start=False, main=False, favorites=False, yes_no=False):
    keyboard = VkKeyboard(one_time=True)
    if start:
        keyboard.add_button('Старт', color=VkKeyboardColor.POSITIVE)
    elif main:
        keyboard.add_button('Ещё', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Стоп', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Добавить в избранное', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Открыть избранное', color=VkKeyboardColor.SECONDARY)
    elif favorites:
        keyboard.add_button('Удалить', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Главное меню', color=VkKeyboardColor.PRIMARY)
    elif yes_no:
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


DELAY = 0.34  # задержка перед запросом к апи

KEYBOARD_start = create_keyboard(start=True)            # Кнопка СТАРТ
KEYBOARD_main = create_keyboard(main=True)              # Главное меню
KEYBOARD_favorites = create_keyboard(favorites=True)    # Меню избранного
KEYBOARD_yes_or_no = create_keyboard(yes_no=True)       # Кнопки ДА НЕТ

if __name__ == '__main__':
    user_api_object = authorize('tokens.ini', my_token=True)  # тут объект, созданный на основе личного токена. От него будут апи-запросы, вроде users.search, photos.get
    generator_of_messages = content_generator('1', user_api_object)

    for message_params in generator_of_messages:
        print(message_params)

