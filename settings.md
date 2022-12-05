### Запуск чат-бота VKinder
1. Создать группу ВКонтакте согласно [инструкции](https://github.com/netology-code/adpy-team-diplom/blob/main/group_settings.md).

2. Cоздать базу данных  c именем vkinder в PostgreSQL.

3. Создать  файл token.ini, в котором в первой строке указать личный токен, во второй строке токен сообщества.
   * Инструкция для получения личного токена находится [здесь](https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit).
   * Получение токена сообщества описано в инструкции из п.1.

4. В файле main.py внести в значение переменной db_password для функции bot свой пароль от PostgreSQL.

После запуска main.py бот начинает работу.

_При необходимости удалить таблицы из базы данных vkinder можно следующим образом:_
* _в файле dbdeliriuminator/classdbinator.py в строке 632 внести свой пароль от PostgreSQL в значение переменной password;_
* _запустить dbdeliriuminator/classdbinator.py._
