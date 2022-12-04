from vkinder_bot import bot
from dbdelirium.configinator import public_token, dbpassword, user_token

if __name__ == '__main__':
    # with open('tokens.ini', 'r', encoding='utf-8') as file:
    #     user_token, public_token = file.readlines()
    bot(user_token=user_token, public_token=public_token, db_password=dbpassword)
