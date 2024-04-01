import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

class Database():
    """ Класс для взаимодействия с базой данных """

    def __init__(self, db_name):
        """ Подключаемся к базе данных """
        self.db = mysql.connector.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PASSWORD, database=db_name)
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        """ Создаем таблицу users """
        try:
            query = ("CREATE TABLE IF NOT EXISTS users("
                     "id INT AUTO_INCREMENT PRIMARY KEY,"
                     "user_block TEXT,"
                     "telegram_id TEXT,"
                     "role TEXT);")
            self.cursor.execute(query)
            self.db.commit()
        except mysql.connector.Error as Error:
            print("Ошибка при создании: ", Error)

    def add_user(self, user_block, telegram_id, has_car):
        """ Добавить пользователя в базу данных """
        self.cursor.execute("INSERT INTO users (user_block, telegram_id, car, role) VALUES (%s, %s, %s, %s)", (user_block, telegram_id, bool(has_car), "user"))
        self.db.commit()
    
    def get_all_users(self):
        """ Получить всех пользователей бд """
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        return users

    def select_user_id(self, telegram_id):
        """ Получам данные пользователя """
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id, ))
        user = self.cursor.fetchone()
        return user
    
    def is_user_admin(self, telegram_id):
        """ Проверят, админ ли пользователь по его telegram_id """
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id, ))
        user = self.cursor.fetchone() # How we can get data in dictionary instead list
        if user[-1] == "admin":
            return user
        else:
            return False

    def __del__(self):
        """ Закрываем подключение к бд """
        self.cursor.close()
        self.db.close()