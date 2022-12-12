from time import sleep


DELAY = 0.34  # задержка перед запросом к апи


def get_user_info(user_name_or_id, my_token_api_object):
    '''
    :param user_name_or_id: id или имя пользователя, например: 1 или paveldurov
    :param my_token_api_object: объект vk_api.VkApi(token=user_token, api_version='5.131').get_api()
    :return: возвращает кортеж данных о пользователе: возраст, город, пол
    '''
    sleep(DELAY)
    user_info = my_token_api_object.users.get(**{'user_ids': user_name_or_id,
                                                 'fields': 'bdate, city, sex'})[0]
    user_birthday = user_info.get('bdate', None) # str
    if user_birthday:
        user_birthday = int(user_birthday[-4:])
    user_city_title = user_info.get('city', {}).get('title', None) # str
    user_sex = user_info['sex']  # int: 1 - женщина, 2 - мужчина
    return bool(user_sex - 1), user_birthday, user_city_title


def find_people(user_sex, user_birth_year, user_city_title, my_token_api_object):
    '''
    :param user_sex: инфо, возвращённое функцией get_user_info
    :param user_age: инфо, возвращённое функцией get_user_info
    :param user_city_title: инфо, возвращённое функцией get_user_info
    :param my_token_api_object: объект vk_api.VkApi(token=user_token, api_version='5.131').get_api()
    :return: список найденных людей
    '''

    sleep(DELAY)
    response = my_token_api_object.users.search(**{'sort': '0',
                                                    'count': '1000',
                                                    'hometown': user_city_title,
                                                    'sex': 1 if user_sex else 2,
                                                    'status': 6,                      # семейное положение, 0 - ВСЁ, 6 — в активном поиске
                                                    'birth_year': user_birth_year,
                                                    'has_photo': '1'})                # строго с фото
    people = response['items']  # тут список найденных людей
    not_closed_profiles = [person for person in people if not person['is_closed']]
    return not_closed_profiles


def content_generator(one_person_list, my_token_api_object):
    '''
    :param one_person_list: список данных о текущей персоне из списка найденных людей для знакомства.
    :param my_token_api_object: vk_api.VkApi(token=user_token, api_version='5.131').get_api()
    :return: Параметры для ВК метода message.send, это для бота
    '''
    person_id = one_person_list[0]
    sleep(DELAY)
    avatars = my_token_api_object.photos.get(**{'owner_id': person_id,
                                                 'album_id': 'profile',
                                                 'rev': '1',            #  берём самые свежие фото
                                                 'extended': '1',
                                                 'count': '1000'})['items']
    avatars.sort(key=lambda x: x['likes']['count'])
    avatars = avatars[-3:]
    three_most_liked = [f'photo{photo["owner_id"]}_{photo["id"]}' for photo in avatars]
    return *one_person_list, three_most_liked


if __name__ == '__main__':
    pass