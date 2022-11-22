import vk_api
from time import sleep
from datetime import datetime


delay = 0.34

with open('tokens.ini', 'r', encoding='utf-8') as file:
    user_token, public_token = file.readlines()

vk_user = vk_api.VkApi(token=user_token, api_version='5.131')

api_user = vk_user.get_api()


def find_people(user):
    sleep(delay)
    user_info = api_user.users.get(**{'user_ids': user,
                                      'fields': 'bdate, city, sex'})[0]
    user_id = user_info['id'] # int
    user_birthday = user_info.get('bdate', None) # str
    user_age = datetime.now().year - int(user_birthday[-4:])
    user_city_title = user_info.get('city', {}).get('title', None) # str
    user_sex = user_info['sex'] # int: 1 - женщина, 2 - мужчина
    if not user_city_title:
        user_city_title = input('Введите Ваш город: ')
    sleep(delay)
    response = api_user.users.search(**{'sort': '0',
                                        'count': '1000',
                                        'hometown': user_city_title,
                                        'sex': 1 if user_sex == 2 else 2,
                                        'status': 6,                      # семейное положение, 0 - ВСЁ, 6 — в активном поиске
                                        'age_from': str(user_age - 3),
                                        'age_to': str(user_age + 3),     # ищем анкеты +-3 года от возраста пользователя
                                        'has_photo': '1'})             # строго с фото
    people = response['items'] # тут список найденных людей
    for person in people:
        if not person['is_closed']:  # closed - закрытый профиль, фотки у такого не собрать
            person_name = f'{person["first_name"]} {person["last_name"]}'
            person_id = person['id']
            person_link = f'https://vk.com/id{person_id}'
            message = f'{person_name}\n{person_link}'
            sleep(delay)
            avatars = api_user.photos.get(**{'owner_id': person_id,
                                             'album_id': 'profile',
                                             'rev': '1',            #  берём самые свежие фото
                                             'extended': '1',
                                             'count': '1000'})['items']
            avatars.sort(key=lambda x: x['likes']['count'])
            avatars = avatars[-3:]
            three_most_liked = [f'photo{photo["owner_id"]}_{photo["id"]}' for photo in avatars] # [max(photo['sizes'], key=lambda x: x['width'])['url'] for photo in avatars]
            attachment = ', '.join(three_most_liked)
            params_of_send_message = {'user_id': user,
                                      'message': message,
                                      'attachment': attachment,
                                  #   'keyboard': ''  тут сделаем кнопку
                                      }
            print(params_of_send_message)
           # yield params_of_send_message



            # next_person = input('Открыть следующую анкету? \n1 - Да\n2 - Нет\n')
            # if next_person == '2':
            #     break


find_people('1')