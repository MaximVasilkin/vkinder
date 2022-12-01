# deliriumdb.py

import psycopg2
import datetime

# Эта функция вставляет пароль и в тест и в класс
# также есть неработающие дубли этой функции и
# пароль можно ввести в класс при инициализации
def getconfig():
    configdict = {'hostname': 'localhost',
                  'username': 'postgres',
                  'password': 'pstpwd',
                  'database': 'vkinder'
                 }
    return configdict


# deliriumdb.py
# узрите, новый делириуминатор

# ---------------------- dbdelirium ---------------------------------------------

class DeliriumBDinator:

    def __init__(self, *, username=None, password=None, database=None):
        """ инициализация класса (self, *, username=None, password=None, database=None)
        по умолчанию настройки берутся из self._getdeliriumdbconfig() """
        if username and password and database:
            self.connection = self._get_connection()
        else:
            self.connection = self._get_connection(username=username,
                                                   password=password,
                                                   database=database)

    #  функции работы с СУБД
    def _getdeliriumdbconfig(self):
        """ Получение настроек для связи с СУБД """
        # configdict = {'hostname': 'localhost',
        #               'username': 'postgres',
        #               'password': '1234',
        #               'database': 'vkinder'
        #               }
        # return configdict
        return getconfig()

    def _get_connection(self, *, username=None, password=None, database=None, hostname='localhost'):
        """ возвращает соединение с СУБД по настройкам возвращаемым
            self._getdeliriumdbconfig"""
        if not (username and password and database):
            dict_data = self._getdeliriumdbconfig()
            hostname = dict_data['hostname']
            username = dict_data['username']
            password = dict_data['password']
            database = dict_data['database']
        self.host = hostname
        self.user = username
        self.password = password
        self.database = database
        result = psycopg2.connect(host=hostname,
                                  user=username,
                                  password=password,
                                  database=database)
        return result

    def close(self):
        if not self.connection.closed:
            self.connection.close()

    def closed(self):
        return self.connection.closed

    # таблица vk_user -------------------------------------------------------------
    def get_user(self, vk_id: int):
        """ данные пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT * FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchone()
        return result

    def get_user_favorites(self, vk_id: int) -> list:
        """ данные об избранных пользователя по vk_id таблицы vk_user """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT * FROM favorites JOIN user_favorites ON favorites.vk_id = user_favorites.favorites_id WHERE user_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchall()
        return result

    def get_user_favorites_id(self, vk_id: int) -> list:
        """ данные о vk_id избранных пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT vk_id FROM favorites JOIN user_favorites ON favorites.vk_id = user_favorites.favorites_id WHERE user_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchall()
        return result


    def add_user(self, vk_id, position=0, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None):
        """ добавляем данные пользователя поля vk_id и date обязательны
        (self, vk_id, date, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None) """
        if date is None:
            date = datetime.datetime.now().timestamp()
        with self.connection, self.connection.cursor() as cursor:
            sql = """INSERT INTO vk_user(vk_id, user_position, user_date, user_name, user_surname, user_birthday, user_age, user_sex, user_city, user_data)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(sql, (vk_id, position, date, name, surname, birthday, age, sex, city, data))

    def delete_user(self, vk_id):
        """ удаляем пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql_1 = "DELETE FROM favorites JOIN user_favorites ON favorites.vk_id = user_favorites.favorites_id WHERE user_id = %s"
            cursor.execute(sql_1, (vk_id,))
            sql_2 = "DELETE FROM user_favorites WHERE user_id = %s"
            cursor.execute(sql_2, (vk_id,))
            sql_3 = "DELETE FROM vk_user WHERE user_id = %s"
            cursor.execute(sql_3, (vk_id,))

    def update_user(self, vk_id, position=None, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None,
                    data=None):
        """ изменяем данные пользователя
        (self, vk_id, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None)"""
        with self.connection, self.connection.cursor() as cursor:
            if position != None:
                cursor.execute("""UPDATE vk_user
                            SET user_position = %s
                            WHERE vk_id = %s;""", (position, vk_id))
            if date:
                cursor.execute("""UPDATE vk_user
                            SET user_date = %s
                            WHERE vk_id = %s;""", (date, vk_id))
            if name:
                cursor.execute("""UPDATE vk_user
                            SET user_name = %s
                            WHERE vk_id = %s;""", (name, vk_id))
            if surname:
                cursor.execute("""UPDATE vk_user
                            SET user_surname = %s
                            WHERE vk_id = %s;""", (surname, vk_id))
            if birthday:
                cursor.execute("""UPDATE vk_user
                            SET user_birthday = %s
                            WHERE vk_id = %s;""", (birthday, vk_id))
            if age:
                cursor.execute("""UPDATE vk_user
                            SET user_age = %s
                            WHERE vk_id = %s;""", (age, vk_id))
            if sex:
                cursor.execute("""UPDATE vk_user
                            SET user_sex = %s
                            WHERE vk_id = %s;""", (sex, vk_id))
            if city:
                cursor.execute("""UPDATE vk_user
                            SET user_city = %s
                            WHERE vk_id = %s;""", (city, vk_id))
            if data:
                cursor.execute("""UPDATE vk_user
                            SET user_data = %s
                            WHERE vk_id = %s;""", (data, vk_id))

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
        """ Проверяет наличие связи пользователя и избранного.
        стоит убрать этот метод ??????????????????????????????????????????????????????????????????????????
        """
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


    def add_favorites(self, user_id, favorites_id, date=None, name=None, surname=None, birthday=None, age=None, sex=None,
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
            if cursor.fetchone():
                return False
            # добавляем в избранное
            sql_insert_f = "INSERT INTO favorites(vk_id, user_date, user_name, user_surname, user_birthday, user_age, user_sex, user_city, user_data, user_photo_1, user_photo_2, user_photo_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(sql_insert_f, (favorites_id, date, name, surname, birthday, age, sex, city, data, photo_1, photo_2, photo_3))
            # добавляем связь
            sql_insert_uf = "INSERT INTO user_favorites(user_id, favorites_id) VALUES (%s, %s)"
            cursor.execute(sql_insert_uf, (user_id, favorites_id))
        return True

    def update_favorites(self, vk_id, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None,
                         data=None,
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
        return  # просто бессмысленный ретурн

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


# ---------- CREATE TABLES and DROP

sql_create_vk_user = """CREATE TABLE IF NOT EXISTS vk_user (
    -- id SERIAL PRIMARY KEY,
    vk_id INTEGER PRIMARY KEY,
    user_position SMALLINT,
    user_date INTEGER NOT NULL,
    user_name VARCHAR(50),
    user_surname VARCHAR(60),
    user_birthday INTEGER,
    user_sex BOOLEAN,
    user_age SMALLINT,
    user_city  VARCHAR(60),
    user_data VARCHAR(60));
"""
sql_create_favorites = """CREATE TABLE IF NOT EXISTS favorites (
    vk_id INTEGER PRIMARY KEY,
    user_date INTEGER NOT NULL,
    user_name VARCHAR(50),
    user_surname VARCHAR(60),
    user_birthday INTEGER,
    user_age SMALLINT,
    user_city  VARCHAR(60),
    user_sex BOOLEAN, -- 0 - male 1 - female
    user_photo_1 VARCHAR(60),
    user_photo_2 VARCHAR(60),
    user_photo_3 VARCHAR(60),
    user_data VARCHAR(60));"""

# -- многие ко многим (1 вариант)
sql_create_u_f = """CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INTEGER REFERENCES vk_user(vk_id),
    favorites_id INTEGER REFERENCES favorites(vk_id),
    CONSTRAINT pk PRIMARY KEY (user_id, favorites_id)
);"""


# def getconfig(): смотри наверху
#     """ Получение настроек для связи с СУБД """
#     configdict = {'hostname': 'localhost',
#                   'username': 'postgres',
#                   'password': '1234',
#                   'database': 'vkinder'
#                   }
#     return configdict


def get_connection(*, username=None, password=None, database=None, hostname='localhost'):
    """ возвращает соединение с СУБД по настройкам возвращаемым
        getconfig """
    if not (username and password and database):
        dict_data = getconfig()
        hostname = dict_data['hostname']
        username = dict_data['username']
        password = dict_data['password']
        database = dict_data['database']
    result = psycopg2.connect(host=hostname,
                              user=username,
                              password=password,
                              database=database)
    return result


def create_tables():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_create_vk_user)
            cursor.execute(sql_create_favorites)
            cursor.execute(sql_create_u_f)
        connection.commit()
    finally:
        connection.close()
    return


def drop_tables():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql_drop_vk_user = """DROP TABLE vk_user;"""
            sql_drop_favorites = """DROP TABLE favorites;"""

            sql_drop_u_f = """DROP TABLE user_favorites;"""
            cursor.execute(sql_drop_u_f)
            cursor.execute(sql_drop_vk_user)
            cursor.execute(sql_drop_favorites)
        connection.commit()
    finally:
        connection.close()


# # tests ---------------------------------------------------------------------------------------------------------
# import pytest
# import random
#
#
# def test_1():
#     try:
#         create_tables()
#
#         vkinder = DeliriumBDinator()
#
#         for user_id in range(1000000000, 1000000100, 10):
#             vkinder.add_user(user_id)
#             for favorit_id in range(user_id - 10, user_id, 2):
#                 vkinder.add_favorites(user_id, favorit_id)
#                 # проверить функцию add_favorites
#         # input('push inter:')
#         for user_id in range(1000000000, 1000000100, 10):
#             print(user_id, vkinder.is_user(user_id))
#             print(not (vkinder.is_user(user_id) is None))
#             for favorit_id in range(user_id - 10, user_id, 2):
#                 print('       ', favorit_id, not (vkinder.is_favorites(favorit_id) is None))
#                 print('       ', not (vkinder.is_user_favorites(user_id, favorit_id) is None))
#         # input('push inter:')
#         for user_id in range(1000000000, 1000000100, 10):
#             assert not (vkinder.is_user(user_id) is None)
#             for favorit_id in range(user_id - 10, user_id, 2):
#                 assert not (vkinder.is_favorites(favorit_id) is None)
#                 assert not (vkinder.is_user_favorites(user_id, favorit_id) is None)
#         vkinder.close()
#
#     finally:
#         drop_tables()
#
#
# # end tests -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    drop_tables()
    create_tables()