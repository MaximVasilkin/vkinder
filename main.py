from vkinder_bot import bot


if __name__ == '__main__':
    with open('tokens.ini', 'r', encoding='utf-8') as file:
        user_token, public_token = file.readlines()
    bot(user_token=user_token, public_token=public_token,
        db_user_name='postgres', db_password='pstpwd', db='vkinder',
        memory_days=1)
