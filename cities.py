import json

def get_city_list(paht):
    with open(paht, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    city_list = []
    city_list_check = []
    for city in templates:
        city_list.append(city['city'])
        city_list_check.append(city['city'].lower().replace('-',' '))
    return city_list_check, city_list
