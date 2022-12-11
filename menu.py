from keyboards import KEYBOARD_start, KEYBOARD_main, KEYBOARD_yes_or_no, KEYBOARD_favorites


class Command:
    START = 'Старт'
    NEXT_PERSON = 'Ещё'
    STOP = 'Стоп'
    ADD_TO_FAVORITE = 'Добавить в избранное'
    OPEN_FAVORITE = 'Открыть избранное'
    DELETE = 'Удалить'
    OPEN_MAIN_MENU = 'Главное меню'
    YES = 'Да'
    NO = 'Нет'


class Position:
    INTRO = 0
    IN_MAIN_MENU = 1
    IN_ADD_FAVORITE_MENU = 2
    IN_FAVORITE_MENU = 3
    IN_DELETE_FAVORITE_MENU = 4
    NEED_AGE = 404
    NEED_CITY = 405

    KEYBOARDS = {INTRO: KEYBOARD_start,                     # Позиция 0. Когда только что пришёл - кнопка СТАРТ
                 IN_MAIN_MENU: KEYBOARD_main,               # Позиция 1. Когда прошёл все проверки и нажал СТАРТ - кнопки: Ещё, Стоп, Добавить в избранное, Открыть избранное
                 IN_ADD_FAVORITE_MENU: KEYBOARD_yes_or_no,  # Позиция 2. Когда нажал Добавить в избранное - кнопки: Да, Нет
                 IN_FAVORITE_MENU: KEYBOARD_favorites,      # Позиция 3. Когда нажал Открыть избранное - кнопки: Удалить, В главное меню
                 IN_DELETE_FAVORITE_MENU: '',               # Позиция 4. Когда просят ввести ID для удаления из избранного
                 NEED_AGE: '',                              # Позиция 404. Когда нет возраста - нет кнопок
                 NEED_CITY: ''}                             # Позиция 405. Когда нет города - нет кнопок

    @classmethod
    def get_keyboard_from_position(self, position):
        return self.KEYBOARDS[position]
