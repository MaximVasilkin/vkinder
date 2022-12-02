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

#  функции соединения с СУБД -----------------------------------------------------------------------------------
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

    def connect(self):
        if not self.connection.closed:
            self.connection = psycopg2.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      database=self.database)
# ---------------------------------------------------------------------------------------------------------------


    # таблица vk_user -------------------------------------------------------------------------------------------
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

    def get_user_favorites_id(self, vk_id: int) -> list: # -------------------------------------------------
        """ данные о vk_id избранных пользователя по vk_id """
        with self.connection, self.connection.cursor() as cursor:
            sql = "SELECT vk_id FROM favorites JOIN user_favorites ON favorites.vk_id = user_favorites.favorites_id WHERE user_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchall()
        return result

    def add_user(self, vk_id, position=None, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None):
        """ добавляем данные пользователя поле vk_id обязательно
        (self, vk_id, date=None, name=None, surname=None, birthday=None, age=None, sex=None, city=None, data=None) """
        if date is None:
            date = datetime.datetime.now().timestamp()
        with self.connection, self.connection.cursor() as cursor:
            sql = """INSERT INTO vk_user(vk_id, user_position, user_date, user_name, user_surname, user_birthday, user_age, user_sex, user_city, user_data)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(sql, (vk_id, position, date, name, surname, birthday, age, sex, city, data))

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
    # ??????????????????????????????????????????????????????????????????????????????????????????????????????????????

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
            if cursor.fetchone() is None:
                # добавляем в избранное
                sql_insert_f = "INSERT INTO favorites(vk_id, user_date, user_name, user_surname, user_birthday, user_age, user_sex, user_city, user_data, user_photo_1, user_photo_2, user_photo_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(sql_insert_f, (favorites_id, date, name, surname, birthday, age, sex, city, data, photo_1, photo_2, photo_3))
            # добавляем связь
            sql_check_2 = "SELECT * FROM user_favorites WHERE user_id = %s AND favorites_id = %s"
            cursor.execute(sql_check_2, (user_id, favorites_id))
            if cursor.fetchone():
                return False
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
            message = f'{result[4]} {result[5]}\n{result[13]}'
            attachments = [photo for photo in result[10:13] if photo]
        return message, attachments, result[2]

    # find people -----------------------------------------------------------------------------

    def add_find_people(self, vk_id, list_of_dicts, date=None):
        """ добавляет список найденных vk_id в список найденных.
        (self, vk_id, find_ids) """
        if date is None:
            date = datetime.datetime.now().timestamp()
        with self.connection, self.connection.cursor() as cursor:
            # проверка наличия записи ------------------------------
            for person in list_of_dicts:
                sql_insert = """INSERT INTO find_people(user_id, find_people_id, seen_flag, find_people_date, user_name, user_surname, user_data)
                                VALUES (%s, %s, %s, %s, %s, %s, %s);"""
                cursor.execute(sql_insert, (vk_id, person['id'], False, date, person["first_name"], person["last_name"], f'https://vk.com/id{person["id"]}'))

    def get_next_person(self, vk_id: int):
        """ получение данных
        (self, vk_id) """

        with self.connection, self.connection.cursor() as cursor:
            sql_select = "SELECT find_people_id, user_name, user_surname, user_data FROM find_people WHERE user_id = %s AND seen_flag = False"
            cursor.execute(sql_select, (vk_id,))
            result = cursor.fetchone()
            if result:                # not SEEN
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

# ---------------------- end dbdelirium  ----------------------------------------------

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

# табоица найденных людей
sql_create_last_send_person = """CREATE TABLE IF NOT EXISTS last_send_person (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES vk_user(vk_id),
    last_id INTEGER NOT NULL,
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

# -- многие ко многим (1 вариант) id-шники
sql_create_find_people = """CREATE TABLE IF NOT EXISTS find_people (
    user_id INTEGER REFERENCES vk_user(vk_id),
    find_people_id INTEGER NOT NULL,
    seen_flag BOOLEAN,
    find_people_date INTEGER NOT NULL,
    user_name VARCHAR(50),
    user_surname VARCHAR(60),
    user_data VARCHAR(60),
    CONSTRAINT pk_fp PRIMARY KEY (user_id, find_people_id)
);"""


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
            cursor.execute(sql_create_last_send_person)
            cursor.execute(sql_create_find_people)
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
            sql_drop_find_people = """DROP TABLE find_people;"""
            sql_drop_last_send_person = """DROP TABLE last_send_person;"""
            cursor.execute(sql_drop_u_f)
            cursor.execute(sql_drop_favorites)
            cursor.execute(sql_drop_find_people)
            cursor.execute(sql_drop_last_send_person)
            cursor.execute(sql_drop_vk_user)
        connection.commit()
    finally:
        connection.close()

def check():
    try:
        create_tables()

        vkinder = DeliriumBDinator()

        # for user_id in range(1000000000, 1000000100, 10):
        #     vkinder.add_user(user_id)
        #     for favorit_id in range(user_id - 14, user_id, 2):
        #         vkinder.add_favorites(user_id, favorit_id)

        u = [1, 2, 3, 4]
        f = [[2, 7, 8, 9], [1, 7, 8, 6], [2, 7, 8, 5], [2, 7, 8, 5]]
        for user, fav in zip(u, f):
            vkinder.add_user(user)
            for f in fav:
                vkinder.add_favorites(user, f)

        input('push inter:')
        vkinder.set_position(1, 1)
        print('Позиция 1:', vkinder.get_position(1))
        vkinder.set_position(1, 2)
        print('Позиция 1:', vkinder.get_position(1))

        print('Фавориты 1:', vkinder.get_user_favorites_id(1))
        print('Фавориты 2:', vkinder.get_user_favorites_id(2))
        print('Фавориты 3:', vkinder.get_user_favorites_id(3))
        print('Фавориты 4:', vkinder.get_user_favorites_id(4))
        print(vkinder.add_favorites(4, 5))
        vkinder.delete_favorites(4, 5)
        print('у 4 удалили 5')
        print('Фавориты 1:', vkinder.get_user_favorites_id(1))
        print('Фавориты 2:', vkinder.get_user_favorites_id(2))
        print('Фавориты 3:', vkinder.get_user_favorites_id(3))
        print('Фавориты 4:', vkinder.get_user_favorites_id(4))
        vkinder.delete_favorites(1, 9)
        print('у 1 удалили 9')
        print('Фавориты 1:', vkinder.get_user_favorites_id(1))
        print('Фавориты 2:', vkinder.get_user_favorites_id(2))
        print('Фавориты 3:', vkinder.get_user_favorites_id(3))
        print('Фавориты 4:', vkinder.get_user_favorites_id(4))
        print(vkinder.is_user_favorites(1, 9))
        vkinder.delete_favorites(3, 5)
        print('у 3 удалили 5')
        print('Фавориты 1:', vkinder.get_user_favorites_id(1))
        print('Фавориты 2:', vkinder.get_user_favorites_id(2))
        print('Фавориты 3:', vkinder.get_user_favorites_id(3))
        print('Фавориты 4:', vkinder.get_user_favorites_id(4))
        print(vkinder.is_user_favorites(3, 5))
        vkinder.delete_user(2)
        print('Фавориты 1:', vkinder.get_user_favorites_id(1))
        print('Фавориты 2:', vkinder.get_user_favorites_id(2))
        print('Фавориты 3:', vkinder.get_user_favorites_id(3))
        print('Фавориты 4:', vkinder.get_user_favorites_id(4))
        vkinder.close()

    finally:
        drop_tables()

# end tests -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    drop_tables()
    create_tables()
