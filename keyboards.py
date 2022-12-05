from vk_api.keyboard import VkKeyboard, VkKeyboardColor


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




KEYBOARD_start = create_keyboard(start=True)            # Кнопка СТАРТ
KEYBOARD_main = create_keyboard(main=True)              # Главное меню
KEYBOARD_favorites = create_keyboard(favorites=True)    # Меню избранного
KEYBOARD_yes_or_no = create_keyboard(yes_no=True)       # Кнопки ДА НЕТ