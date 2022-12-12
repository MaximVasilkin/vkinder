
# узрите, новый датабейзаинатор

import psycopg2
import datetime
from db.createdatabase import SQL_CREATE_TABLES, SQL_DROP_TABLES

PASSWORD = '1234'

# декораторы --------------------------------------------------------------------------------------
def trycloseinator(method):
    ''' Декоратор, декорирующий функции класс БД таким образом, что если
    флаг self.tryclosemode = True при каждом вызове мотеда класса происходит
    соединение с СУБД и закрытие соединенияю '''
    def wrapper(self, *args, **kwargs):
        if self.tryclosemode:
            try:
                self.connect()
                result = method(self, *args, **kwargs)
            finally:
                self.close()
                return result
        else:
            return method(self, *args, **kwargs)
    return wrapper

def decor_methods_dbinator(decorator):
    """ Применяет полученный декоратор к методам класса DataBaseInator
    по определенному условию или списку """
    list_attr = ['get_user', 'get_user_additional_age', 'get_user_favorites',
                 'get_user_favorites_id', 'add_user', 'delete_user', 'update_user',
                 'set_position', 'get_position', 'is_user', 'is_favorites',
                 'is_user_favorites', 'get_favorites', 'add_favorites', 'update_favorites',
                 'delete_favorites', 'set_last_send_person', 'get_last_send_person', 'delete_last_send_person',
                 'add_find_people', 'get_next_person', 'is_find_people', 'delete_find_people']

    def decorate(mydbclass):
        for attr in list_attr:
            setattr(mydbclass, attr, decorator(getattr(mydbclass, attr)))
        return mydbclass
    return decorate

# ---------------------- db ---------------------------------------------
@decor_methods_dbinator(trycloseinator)
class DataBaseInator:

    def __init__(self, username='postgres', password='1234', database='vkinder', host='localhost', **kwargs):
        """ инициализация класса (username='postgres', password='1234', database='vkinder', host='localhost', **kwargs)
        tryclosemode=True включает режим tryclose - коннект и закрытие коннекта при каждом вызове метода
        """
        if kwargs.get('tryclosemode', None) is None:
            self.tryclosemode = False
        else:
            self.tryclosemode = True
            kwargs.pop('tryclosemode')
        self.user = username
        self.password = password
        self.database = database
        self.host = host
        self.kwargs = kwargs
        self.connection = None
        # self.connect()

#  функции соединения с СУБД -----------------------------------------------------------------------------------

    def connect(self):
        ''' соединение с СУБД '''
        if not self.connection or self.connection.closed:
            self.connection = psycopg2.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      database=self.database,
                                      **self.kwargs)

    def close(self):
        ''' закрытие соединения '''
        if not self.connection.closed:
            self.connection.close()


    def closed(self):
        return self.connection.closed

    # таблица vk_user -------------------------------------------------------------------------------------------
    def get_user(self, vk_id: int):
        """ данные пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT * FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchone()
        return result

    def get_user_additional_age(self, vk_id: int):
        """ данные пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT user_age_range FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchone()[0]
            if result:
                range_list = result.split()
                item = range_list.pop()
                new_range_ages = ' '.join(range_list)
                cursor.execute("""UPDATE vk_user
                                     SET user_age_range = %s
                                   WHERE vk_id = %s;""", (new_range_ages, vk_id))
                return item

    # create drop tables ----------------------------------------------------------------------------------------
    def create_tables(self):
        """ создание таблиц """
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(SQL_CREATE_TABLES)

    def drop_tables(self):
        """ удаление таблиц """
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(SQL_DROP_TABLES)
    # -------------------------------------------------------------------------------------------------------------

    def get_user_favorites(self, vk_id: int) -> list:
        """ данные об избранных пользователя по vk_id таблицы vk_user """
        with self.connection, self.connection.cursor() as cursor:
            sql = '''SELECT * FROM favorites 
                       JOIN user_favorites 
                         ON favorites.vk_id = user_favorites.favorites_id 
                      WHERE user_id = %s'''
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchall()
        return result

    def get_user_favorites_id(self, vk_id: int) -> list: # -------------------------------------------------
        """ данные о vk_id избранных пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql = '''SELECT vk_id FROM favorites 
                       JOIN user_favorites 
                         ON favorites.vk_id = user_favorites.favorites_id 
                      WHERE user_id = %s'''
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchall()
        return result

    def add_user(self, vk_id, position=None, date=None, name=None, surname=None, birthday=None, age_range=None, sex=None, city=None, data=None):
        """ добавляем данные пользователя поле vk_id обязательно
        (self, vk_id, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None) """
        if date is None:
            date = datetime.datetime.now().timestamp()
        with self.connection, self.connection.cursor() as cursor:
            sql = """INSERT INTO vk_user(vk_id, user_position, user_date, user_name, user_surname, 
                                         user_birthday, user_age_range, user_sex, user_city, user_data)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(sql, (vk_id, position, date, name, surname, birthday, age_range, sex, city, data))

    def delete_user(self, vk_id):
        """ удаляем пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql_2 = "DELETE FROM user_favorites WHERE user_id = %s"
            cursor.execute(sql_2, (vk_id,))
            sql_3 = "DELETE FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql_3, (vk_id,))
        with self.connection, self.connection.cursor() as cursor:
            sql_1 = """DELETE FROM favorites 
                        WHERE vk_id IN
                        (SELECT vk_id FROM favorites JOIN user_favorites ON favorites.vk_id = user_favorites.favorites_id
                        WHERE user_favorites.favorites_id IS NULL);"""
            cursor.execute(sql_1, (vk_id,))

    def update_user(self, vk_id, position=None, date=None, name=None, surname=None,
                    birthday=None, age_range=None, sex=None, city=None, data=None):
        """ изменяем данные пользователя
        (self, vk_id, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None)"""
        with self.connection, self.connection.cursor() as cursor:
            if position is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_position = %s
                                        WHERE vk_id = %s;""", (position, vk_id))
            if date is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_date = %s
                                        WHERE vk_id = %s;""", (date, vk_id))
            if name is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_name = %s
                                        WHERE vk_id = %s;""", (name, vk_id))
            if surname is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_surname = %s
                                        WHERE vk_id = %s;""", (surname, vk_id))
            if birthday is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_birthday = %s
                                        WHERE vk_id = %s;""", (birthday, vk_id))
            if age_range is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_age_range = %s
                                        WHERE vk_id = %s;""", (age_range, vk_id))
            if sex is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_sex = %s
                                        WHERE vk_id = %s;""", (sex, vk_id))
            if city is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_city = %s
                                        WHERE vk_id = %s;""", (city, vk_id))
            if data is not None:
                cursor.execute("""UPDATE vk_user
                                        SET user_data = %s
                                        WHERE vk_id = %s;""", (data, vk_id))

    # Позиции .................................................................................................
    def set_position(self, vk_id, position):
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute("""UPDATE vk_user
                            SET user_position = %s
                            WHERE vk_id = %s;""", (position, vk_id))

    def get_position(self, vk_id):
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute("""SELECT user_position
                                FROM vk_user
                                WHERE vk_id = %s;""", (vk_id,))
            result = cursor.fetchone()
            return result[0]

    # ????????????????????????????????????????????????????????????????????????????????????????????????????????????
    def is_user(self, user_id):
        """ Проверяет наличие пользователя. Возвращает id пользователя либо None.
        Дублирует частично по функционалы метод get_user """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT vk_id FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
        return result

    def is_favorites(self, favorites_id):
        """ Проверяет наличие избранного. Возвращает id пользователя либо None.
        Дублирует частично по функционалы метод get_favorites """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT vk_id FROM favorites WHERE vk_id = %s"
            cursor.execute(sql, (favorites_id,))
            result = cursor.fetchone()
        return result

    def is_user_favorites(self, user_id, favorites_id):
        """ Проверяет наличие связи пользователя и избранного. """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT user_id, favorites_id FROM user_favorites WHERE user_id = %s AND favorites_id = %s"
            cursor.execute(sql, (user_id, favorites_id,))
            result = cursor.fetchone()
        return result


    def get_favorites(self, vk_id):
        """  данные избранного по vk_id favorites """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT * FROM favorites WHERE vk_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchone()
        return result
    # ??????????????????????????????????????????????????????????????????????????????????????????????????????????????

    def add_favorites(self, user_id, favorites_id, date=None, name=None,
                      surname=None, birthday=None, age=None, sex=None,
                      city=None, data=None, photo_1=None, photo_2=None, photo_3=None):
        """ Добавляет пользователя в избранное. Если не удалось добавить, возвращает False
        Проверяет равенство user_id, favorites_id и наличие favorites_id в БД """
        if date is None:
            date = datetime.datetime.now().timestamp()
        if user_id == favorites_id:
            return False
            # raise ErrorEquelId
        with self.connection, self.connection.cursor() as cursor:
            # проверка наличия пользователя в избранном ------------------------------
            sql_check = "SELECT vk_id FROM favorites WHERE vk_id = %s"
            cursor.execute(sql_check, (favorites_id,))
            if cursor.fetchone() is None:
                # добавляем в избранное
                sql_insert_f = '''INSERT INTO favorites(vk_id, user_date, user_name, user_surname, user_birthday, 
                                                        user_age, user_sex, user_city, user_data, user_photo_1, 
                                                        user_photo_2, user_photo_3) 
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
                cursor.execute(sql_insert_f, (favorites_id, date, name, surname, birthday,
                                              age, sex, city, data, photo_1, photo_2, photo_3))
            # добавляем связь
            sql_check_2 = "SELECT * FROM user_favorites WHERE user_id = %s AND favorites_id = %s"
            cursor.execute(sql_check_2, (user_id, favorites_id))
            if cursor.fetchone():
                return False
            sql_insert_uf = "INSERT INTO user_favorites(user_id, favorites_id) VALUES (%s, %s)"
            cursor.execute(sql_insert_uf, (user_id, favorites_id))
        return True

    def update_favorites(self, vk_id, date=None, name=None, surname=None, birthday=None,
                         age=None, sex=None, city=None, data=None,
                         photo_1=None, photo_2=None, photo_3=None):
        """ изменение данных избранного (Нео, приготовься)
        (self, vk_id, date, name=None, surname=None, birthday=None, age=None,
        sex=None, city=None, data=None,
        photo_1=None, photo_2=None, photo_3=None)"""
        with self.connection, self.connection.cursor() as cursor:
            if date:
                cursor.execute("""UPDATE favorites
                            SET user_date = %s
                            WHERE id = %s;""", (date, vk_id))
            if name:
                cursor.execute("""UPDATE favorites
                            SET user_name = %s
                            WHERE id = %s;""", (name, vk_id))
            if surname:
                cursor.execute("""UPDATE favorites
                            SET user_surname = %s
                            WHERE id = %s;""", (surname, vk_id))
            if birthday:
                cursor.execute("""UPDATE favorites
                            SET user_birthday = %s
                            WHERE id = %s;""", (birthday, vk_id))
            if age:
                cursor.execute("""UPDATE favorites
                            SET user_age = %s
                            WHERE id = %s;""", (age, vk_id))
            if sex:
                cursor.execute("""UPDATE favorites
                            SET user_sex = %s
                            WHERE id = %s;""", (sex, vk_id))
            if city:
                cursor.execute("""UPDATE favorites
                            SET user_city = %s
                            WHERE id = %s;""", (city, vk_id))
            if data:
                cursor.execute("""UPDATE favorites
                            SET user_data = %s
                            WHERE id = %s;""", (data, vk_id))
            if photo_1:
                cursor.execute("""UPDATE favorites
                            SET user_photo_1 = %s
                            WHERE id = %s;""", (photo_1, vk_id))
            if photo_2:
                cursor.execute("""UPDATE favorites
                            SET user_photo_2 = %s
                            WHERE id = %s;""", (photo_2, vk_id))
            if photo_3:
                cursor.execute("""UPDATE favorites
                            SET user_photo_3 = %s
                            WHERE id = %s;""", (photo_3, vk_id))


    def delete_favorites(self, user_id, favorites_id):
        """ Удалает пользователя из избранного пользователя.
        Проверяет равенство user_id, favorites_id и наличие favorites_id в БД """
        if user_id == favorites_id:
            return False
            # raise ErrorEquelId
        with self.connection, self.connection.cursor() as cursor:
            # проверка наличия связи пользователя и пользователя (ужс) ------------------------------
            sql_search = "SELECT * FROM user_favorites WHERE user_id = %s AND favorites_id=%s;"
            cursor.execute(sql_search, (user_id, favorites_id))
            if cursor.fetchone() is None:
                return False
            # удаляем взаимосвязь (кшмр)
            sql_delete_uf = "DELETE FROM user_favorites WHERE user_id = %s AND favorites_id=%s;"
            cursor.execute(sql_delete_uf, (user_id, favorites_id))
            # проверяем на наличие сторонних связей (ужс ужс)
            sql_search = "SELECT * FROM user_favorites WHERE user_id <> %s AND favorites_id=%s;"
            cursor.execute(sql_search, (user_id, favorites_id))
            if cursor.fetchone():
                return True
            # удаляем фаворита (именем Е.В.)
            sql_delete_f = "DELETE FROM favorites WHERE vk_id = %s;"
            cursor.execute(sql_delete_f, (favorites_id,))
        return True

    # last person ---------------------------------------------------------------
    def set_last_send_person(self, user_id, last_id, date=None, name=None,
                             surname=None, birthday=None, age=None, sex=None, city=None,
                             data=None, photo_1=None, photo_2=None, photo_3=None):
        """ добавление последнего просмотренного
        (self, user_id, last_id, date=None, name=None,
        surname=None, birthday=None, age=None, sex=None, city=None,
        data=None, photo_1=None, photo_2=None, photo_3=None)"""
        if date is None:
            date = datetime.datetime.now().timestamp()
        if user_id == last_id:
            return False
            # raise ErrorEquelId
        with self.connection, self.connection.cursor() as cursor:
            # проверка наличия записи ------------------------------
            sql_check = "SELECT user_id FROM last_send_person WHERE user_id = %s"
            cursor.execute(sql_check, (user_id,))
            if cursor.fetchone() is None:
                # добавляем пользователя
                sql_insert = """INSERT INTO last_send_person(user_id, last_id, 
                                user_date, user_name, user_surname, user_birthday,
                                user_age, user_sex, user_city, user_data,
                                user_photo_1, user_photo_2, user_photo_3) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                cursor.execute(sql_insert, (user_id, last_id, date, name, surname,
                                            birthday, age, sex, city, data, photo_1, photo_2, photo_3))
                return True
            sql_update = """UPDATE last_send_person
                                SET last_id = %s, 
                                user_date = %s, user_name = %s, user_surname = %s, user_birthday = %s,
                                user_age = %s, user_sex = %s, user_city = %s, user_data = %s,
                                user_photo_1 = %s, user_photo_2 = %s, user_photo_3 = %s
                                WHERE user_id = %s;"""
            cursor.execute(sql_update, (last_id, date, name, surname,
                                        birthday, age, sex, city, data, photo_1, photo_2, photo_3, user_id))
        return True

    def get_last_send_person(self, user_id):
        """ получение данных последнего просмотренного
        (self, user_id) """

        with self.connection, self.connection.cursor() as cursor:
            # проверка наличия записи ------------------------------
            sql_select = "SELECT * FROM last_send_person WHERE user_id = %s"
            cursor.execute(sql_select, (user_id,))
            result = cursor.fetchone()
            name = result[4]
            surname = result[5]
            link = result[13]
            message = f'{name} {surname}\n{link}'
            attachments = [photo for photo in result[10:13] if photo]
            id_ = result[2]
        return message, attachments, id_

    def delete_last_send_person(self, vk_id):
        with self.connection, self.connection.cursor() as cursor:
            sql = "DELETE FROM last_send_person WHERE user_id = %s"
            cursor.execute(sql, (vk_id,))

    # find people -----------------------------------------------------------------------------

    def add_find_people(self, vk_id, list_of_dicts, date=None):
        """ добавляет список найденных vk_id в список найденных.
        (self, vk_id, find_ids) """
        if date is None:
            date = datetime.datetime.now().timestamp()
        with self.connection, self.connection.cursor() as cursor:
            # проверка наличия записи ------------------------------
            for person in list_of_dicts:
                sql_insert = """INSERT INTO find_people(user_id, find_people_id, seen_flag, find_people_date, 
                                                        user_name, user_surname, user_data)
                                VALUES (%s, %s, %s, %s, %s, %s, %s);"""
                cursor.execute(sql_insert, (vk_id, person['id'], False, date, person["first_name"],
                                            person["last_name"], f'https://vk.com/id{person["id"]}'))

    def get_next_person(self, vk_id: int, check=False):
        """ получение данных
        (self, vk_id) """

        with self.connection, self.connection.cursor() as cursor:
            sql_select = '''SELECT find_people_id, user_name, user_surname, user_data 
                              FROM find_people 
                             WHERE user_id = %s AND seen_flag = False'''
            cursor.execute(sql_select, (vk_id,))
            result = cursor.fetchone()
            if result and not check:                # not SEEN
                sql_mark_as_seen = "UPDATE find_people SET seen_flag = True WHERE user_id = %s AND find_people_id = %s"
                cursor.execute(sql_mark_as_seen, (vk_id, result[0]))

        return result

    def is_find_people(self, user_id: int, last_id: int):
        """ проверка наличия id в найденных у пользователя
        (self, vk_id) """
        with self.connection, self.connection.cursor() as cursor:
            sql_select = "SELECT last_id FROM find_people WHERE user_id = %s AND last_id=%s"
            cursor.execute(sql_select, (user_id, last_id))
            result = cursor.fetchone()
        return result

    def delete_find_people(self, vk_id):
        with self.connection, self.connection.cursor() as cursor:
            sql = "DELETE FROM find_people WHERE user_id = %s"
            cursor.execute(sql, (vk_id,))


# ---------------------- end db  ----------------------------------------------

# end tests -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass

