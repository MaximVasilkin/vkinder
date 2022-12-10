from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_keyboard(dict_of_buttons):
    colors = {'green': VkKeyboardColor.POSITIVE,
              'red': VkKeyboardColor.NEGATIVE,
              'blue': VkKeyboardColor.PRIMARY,
              'white': VkKeyboardColor.SECONDARY}
    keyboard = VkKeyboard(one_time=True)
    for button, color in dict_of_buttons.items():
        if not button:
            keyboard.add_line()
        else:
            keyboard.add_button(button, color=colors[color])
    return keyboard.get_keyboard()


KEYBOARD_start = create_keyboard({'Старт': 'green'})

KEYBOARD_main = create_keyboard({'Ещё': 'green',
                                 'Стоп': 'red',
                                 None: None,
                                 'Добавить в избранное': 'blue',
                                 'Открыть избранное': 'white'})

KEYBOARD_favorites = create_keyboard({'Удалить': 'red',
                                      'Главное меню': 'blue'})

KEYBOARD_yes_or_no = create_keyboard({'Да': 'green',
                                      'Нет': 'red'})