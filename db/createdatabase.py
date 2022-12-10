# ---------- CREATE TABLES and DROP ---------------------------------------------------
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

# -- один ко многим id-шники
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

SQL_CREATE_TABLES = [(sql_create_vk_user,),
                     (sql_create_favorites,),
                     (sql_create_u_f,),
                     (sql_create_last_send_person,),
                     (sql_create_find_people,)]

sql_drop_vk_user = """DROP TABLE vk_user;"""
sql_drop_favorites = """DROP TABLE favorites;"""
sql_drop_u_f = """DROP TABLE user_favorites;"""
sql_drop_find_people = """DROP TABLE find_people;"""
sql_drop_last_send_person = """DROP TABLE last_send_person;"""

SQL_DROP_TABLES = [(sql_drop_u_f,),
                     (sql_drop_favorites,),
                     (sql_drop_find_people),
                     (sql_drop_last_send_person,),
                     (sql_drop_vk_user,)]

def get_connection(*, username='postgres', password=PASSWORD, database='vkinder', hostname='localhost'):
    """ возвращает соединение с СУБД по настройкам возвращаемым """

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
            cursor.execute(sql_drop_u_f)
            cursor.execute(sql_drop_favorites)
            cursor.execute(sql_drop_find_people)
            cursor.execute(sql_drop_last_send_person)
            cursor.execute(sql_drop_vk_user)
        connection.commit()
    finally:
        connection.close()