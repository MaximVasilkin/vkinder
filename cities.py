import json

def get_city_list(paht):
    with open(paht, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    city_list = []
    for city in templates:
        city_list.append(city['city'])
    return city_list

