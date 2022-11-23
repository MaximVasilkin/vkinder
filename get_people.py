import vk_api
from time import sleep
from datetime import datetime


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
        TOKEN = user_token
    elif bot_token:
        TOKEN = public_token
    return vk_api.VkApi(token=TOKEN, api_version='5.131').get_api()



def find_people(user_name_or_id, my_token_api_object):
    '''
    :param user_name_or_id: id или имя пользователя, например: 1 или paveldurov
    :param my_token_api_object: объект, возвращенный от функции authorize(path, my_token=True)
    :return: id того, кто написал боту, и список найденных ему людей
    '''

    sleep(DELAY)
    user_info = my_token_api_object.users.get(**{'user_ids': user_name_or_id,
                                      'fields': 'bdate, city, sex'})[0]
    user_id = user_info['id']  # int
    user_birthday = user_info.get('bdate', None) # str
    user_age = datetime.now().year - int(user_birthday[-4:])
    user_city_title = user_info.get('city', {}).get('title', None) # str
    user_sex = user_info['sex']  # int: 1 - женщина, 2 - мужчина

    if not user_city_title:
        user_city_title = input('Введите Ваш город: ')  # это надо адаптировать под бота

    sleep(DELAY)
    response = my_token_api_object.users.search(**{'sort': '0',
                                                    'count': '1000',
                                                    'hometown': user_city_title,
                                                    'sex': 1 if user_sex == 2 else 2,
                                                    'status': 6,                      # семейное положение, 0 - ВСЁ, 6 — в активном поиске
                                                    'age_from': str(user_age - 3),
                                                    'age_to': str(user_age + 3),     # ищем анкеты +-3 года от возраста пользователя
                                                    'has_photo': '1'})             # строго с фото
    people = response['items'] # тут список найденных людей
    return user_id, people


def create_message_for_bot(user_id, list_of_people, my_token_api_object):
    '''
    :param user_id: тут id того, кто написал боту
    :param list_of_people: список найденных людей для знакомства
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
            attachment = ', '.join(three_most_liked)
            params_of_message_send = {'user_id': user_id,
                                      'message': message,
                                      'attachment': attachment,
                                  #   'keyboard': ''  тут сделаем кнопку для бота
                                      }
            yield params_of_message_send

            # next_person = input('Открыть следующую анкету? \n1 - Да\n2 - Нет\n')
            # if next_person == '2':
            #     break


DELAY = 0.34  # задержка перед запросом к апи

if __name__ == '__main__':
    user_api_object = authorize('tokens.ini', my_token=True)  # тут объект, созданный на основе личного токена. От него будут апи-запросы, вроде users.search, photos.get

    user_id, list_of_people = find_people('1', user_api_object) # тут id того, кто написал боту, и список найденных ему людей
    generator_of_messages = create_message_for_bot(user_id, list_of_people, user_api_object)

    for message_params in generator_of_messages:
        print(message_params)

