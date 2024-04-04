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
        self.create_users_table()
        self.create_users_car_table()

    def create_users_table(self):
        """ Создаем таблицу users """
        try:
            query = ("CREATE TABLE IF NOT EXISTS users("
                     "id INT AUTO_INCREMENT PRIMARY KEY,"
                     "telegram_id INT UNIQUE,"
                     "user_block TEXT,"
                     "car BOOL NOT NULL,"
                     "role TEXT);")
            self.cursor.execute(query)
            self.db.commit()
        except mysql.connector.Error as Error:
            print("Ошибка при создании: ", Error)
    
    def create_users_car_table(self):
        """ Создаем таблицу users_cars """
        try:
            query = ("CREATE TABLE IF NOT EXISTS users_cars("
                     "id INT AUTO_INCREMENT PRIMARY KEY,"
                     "telegram_id INT,"
                     "car_mark TEXT,"
                     "car_number TEXT,"
                     "CONSTRAINT FK_telegram_id FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)"
                     "ON UPDATE CASCADE ON DELETE CASCADE);")
            self.cursor.execute(query)
            self.db.commit()
        except mysql.connector.Error as Error:
            print("Ошибка при создании: ", Error)

    def add_user(self, user_block, telegram_id, has_car=False, car_mark=None, car_number=None):
        """ Добавить пользователя в базу данных """
        self.cursor.execute("INSERT INTO users (telegram_id, user_block, car, role) VALUES (%s, %s, %s, %s)", (int(telegram_id), user_block, has_car, "user"))

        if has_car and car_mark and car_number:
            self.cursor.execute("INSERT INTO users_cars (telegram_id, car_mark, car_number) VALUES (%s, %s, %s)", (int(telegram_id), car_mark, car_number))

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