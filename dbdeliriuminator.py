
import psycopg2


#  функции работы с СУБД
def deliriumdbconfig():
    configdict = {  'hostname': 'localhost',
                    'username': 'postgres',
                    'password': '1234',
                    'database': 'vkinder'
                 }
    return configdict


def get_connection():
    dict_data = deliriumdbconfig()
    hostname = dict_data['hostname']
    username = dict_data['username']
    password = dict_data['password']
    database = dict_data['database']
    result = psycopg2.connect(host=hostname,
                              user=username,
                              password=password,
                              database=database)
    return result


def get_user(vk_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result


def get_favorites(vk_id):

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM favorites WHERE vk_id IN (SELECT favorites_id FROM user_favorites WHERE user_id = %s)"
            cursor.execute(sql, (vk_id,))
            result = cursor.fetchall()
    finally:
        connection.close()
    return result


def add_user(vk_id, name=None, surname=None, birthday=None, age=None, city=None, data=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO vk_user(vk_id) VALUES (%s);"
            cursor.execute(sql, (vk_id,))
        connection.commit()
    finally:
        connection.close()
    return


def update_user(vk_id, name=None, surname=None, birthday=None, age=None, city=None, data=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if name:
                cursor.execute("""UPDATE vk_user
                            SET user_name = %s
                            WHERE id = %s;""", (name, vk_id))
            if surname:
                cursor.execute("""UPDATE vk_user
                            SET user_surname = %s
                            WHERE id = %s;""", (surname, vk_id))
            if birthday:
                cursor.execute("""UPDATE vk_user
                            SET user_birthday = %s
                            WHERE id = %s;""", (birthday, vk_id))
            if age:
                cursor.execute("""UPDATE vk_user
                            SET user_age = %s
                            WHERE id = %s;""", (age, vk_id))
            if city:
                cursor.execute("""UPDATE vk_user
                            SET user_city = %s
                            WHERE id = %s;""", (city, vk_id))
            if data:
                cursor.execute("""UPDATE vk_user
                            SET user_data = %s
                            WHERE id = %s;""", (data, vk_id))
        connection.commit()
    finally:
        connection.close()


def is_user(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT vk_id FROM vk_user WHERE vk_id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result


def is_favorites(favorites_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT vk_id FROM favorites WHERE vk_id = %s"
            cursor.execute(sql, (favorites_id,))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result


def is_user_favorites(user_id, favorites_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT user_id, favorites_id FROM user_favorites WHERE user_id = %s AND favorites_id = %s"
            cursor.execute(sql, (user_id, favorites_id,))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result


def add_favorites(user_id, favorites_id, name=None, surname=None, birthday=None, age=None, city=None, data=None):
    if user_id == favorites_id:
        return False
        # raise ErrorEquelId
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT vk_id FROM favorites WHERE vk_id = %s"
            cursor.execute(sql, (favorites_id,))
            if not cursor.fetchone():
                sql = "INSERT INTO favorites(vk_id) VALUES (%s);"
                cursor.execute(sql, (favorites_id,))
                connection.commit()
            sql = "SELECT user_id, favorites_id FROM user_favorites WHERE user_id = %s AND favorites_id = %s"
            cursor.execute(sql, (user_id, favorites_id,))
            if cursor.fetchone():
                return False
            sql = "INSERT INTO user_favorites(user_id, favorites_id) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, favorites_id,))
        connection.commit()
    finally:
        connection.close()
    return True


def update_favorites(vk_id, name=None, surname=None, birthday=None, age=None,
                     city=None, data=None, photo_1=None, photo_2=None, photo_3=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
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
        connection.commit()
    finally:
        connection.close()
    return
# ---------------------- end dbdelirium  ----------------------------------------------

# ---------- CREATE TABLES and DROP

sql_create_vk_user = """CREATE TABLE IF NOT EXISTS vk_user (
    -- id SERIAL PRIMARY KEY,
    vk_id INTEGER PRIMARY KEY,
    user_name VARCHAR(50),
    user_surname VARCHAR(60),
    user_age SMALLINT,
    user_born INTEGER,
    user_city  VARCHAR(60),
    user_sex SMALLINT,
    user_data VARCHAR(60));
"""
sql_create_favorites = """CREATE TABLE IF NOT EXISTS favorites (
    vk_id INTEGER PRIMARY KEY,
    user_name VARCHAR(50),
    user_surname VARCHAR(60),
    user_born INTEGER,
    user_age SMALLINT,
    user_city  VARCHAR(60),
    user_sex SMALLINT,
    user_photo_1 VARCHAR(60),
    user_photo_2 VARCHAR(60),
    user_photo_3 VARCHAR(60),
    user_data VARCHAR(60));"""

# -- многие ко многим (1 вариант)
sql_create_u_f =  """CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INTEGER REFERENCES vk_user(vk_id),
    favorites_id INTEGER REFERENCES favorites(vk_id),
    CONSTRAINT pk PRIMARY KEY (user_id, favorites_id)
);"""
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
    return

#______________________Правки Макса_____________________


def is_user_favorites(user_id, favorites_id=False):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if favorites_id:
                sql = "SELECT user_id, favorites_id FROM user_favorites WHERE user_id = %s AND favorites_id = %s"
                cursor.execute(sql, (user_id, favorites_id,))
            else:
                sql = "SELECT user_id FROM user_favorites WHERE user_id = %s;"
                cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result


def delete_from_favorites(user_id, favorite_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql_u_f = 'DELETE FROM user_favorites WHERE user_id = %s AND favorites_id = %s;'
            cursor.execute(sql_u_f, (user_id, favorite_id))
            sql_check = 'SELECT user_favorites.user_id FROM user_favorites JOIN favorites ON user_favorites.favorites_id = favorites.vk_id WHERE user_favorites.favorites_id = %s;'
            cursor.execute(sql_check, (favorite_id,))
            check_in_other_favorites = cursor.fetchone()
            if not check_in_other_favorites:
                sql_f = 'DELETE FROM favorites WHERE vk_id = %s;'
                cursor.execute(sql_f, (favorite_id,))
            connection.commit()
    finally:
        connection.close()


if __name__ == '__main__':
    delete_from_favorites(2, 532338892)
