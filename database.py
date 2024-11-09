import os

from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv


load_dotenv()
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")


class Database:
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
                     "user_block_number INT NOT NULL,"
                     "car BOOL NOT NULL,"
                     "role TEXT,"
                     "user_block_letter NVARCHAR(1) NOT NULL);")
            self.cursor.execute(query)
            self.db.commit()
        except mysql.connector.Error as Error:
            print("Ошибка при создании: ", Error)
            
            
    def create_users_car_table(self):
        """ Создаем таблицу users_cars """
        
        try:
            query = ("CREATE TABLE IF NOT EXISTS users_cars("
                     "telegram_id INT PRIMARY KEY UNIQUE,"
                     "car_mark TEXT,"
                     "car_number TEXT,"
                     "FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)"
                     "ON UPDATE CASCADE ON DELETE CASCADE);")
            self.cursor.execute(query)
            self.db.commit()
        except mysql.connector.Error as Error:
            print("Ошибка при создании: ", Error)
            
            
    def add_user(self, user_block, telegram_id, has_car=False, car_mark=None, car_number=None):
        """ Добавить пользователя в базу данных """
        user_block_number = int(user_block[:-1])
        user_block_letter = user_block[-1:]
        try:
            self.cursor.execute("INSERT INTO users (telegram_id, user_block_number, user_block_letter, car, role) VALUES (%s, %s, %s, %s, %s)", (int(telegram_id), user_block_number, user_block_letter, has_car, "user"))

            if has_car and car_mark and car_number:
                self.cursor.execute("INSERT INTO users_cars (telegram_id, car_mark, car_number) VALUES (%s, %s, %s)", (int(telegram_id), car_mark, car_number))

            self.db.commit()
        except:
            print("Что-то пошло не так!")
            return False
        
        return True
        
        
    def get_all_users(self):
        """ Получить всех пользователей бд """
        
        try:
            self.cursor.execute("SELECT * FROM users")
            users = self.cursor.fetchall()
        except:
            print("Что-то пошло не так!")
            return False
        
        return users
    
    
    def get_all_users_with_car(self):
        """ Получает всех пользователей бд, у которых есть машина """
        
        try:
            query = "SELECT id, telegram_id, user_block_number, user_block_letter role, car_mark, car_number FROM users INNER JOIN users_cars ON users.telegram_id = users_cars.telegram_id;"
            
            self.cursor.execute(query)
            users = self.cursor.fetchall()
        except:
            print("Что-то пошло не так!")
            return False
        
        return users
    
    
    def get_user_by_car_number(self, car_number):
        """ Получает пользователя с определенным номером машины """
        
        try:
            query = "SELECT id, telegram_id, user_block_number, user_block_letter, role, car_mark, car_number FROM users JOIN users_cars ON users.telegram_id = users_cars.telegram_id WHERE car_number = %s"
            
            self.cursor.execute(query, (car_number, ))
            user = self.cursor.fetchone()
        except:
            print("Что-то пошло не так!")
            return False
        
        return user
    
    
    def select_user_id(self, telegram_id):
        """ Получам данные пользователя """
        
        try:
            self.cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id, ))
            user = self.cursor.fetchone()
        except:
            print("Что-то пошло не так!")
            return False
        
        return user
    
    
    def is_user_admin(self, telegram_id):
        """ Проверят, админ ли пользователь по его telegram_id """
        
        try:
            self.cursor.execute("SELECT role FROM users WHERE telegram_id = %s", (telegram_id, ))
            user = self.cursor.fetchone()
        except:
            print("Что-то пошло не так!")
            return False
        
        if user[0] == "admin": # index bug
            return user
        else:
            return False
        
        
    def can_change_block(self, telegram_id):
        """ Функция, проверяющая, можно ли изменить блок """
        
        self.cursor.execute("SELECT last_block_change FROM users WHERE telegram_id = %s", (telegram_id,))
        result = self.cursor.fetchone()
        if result:
            last_change_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_change_time >= timedelta(days=7):
                return True
        return False
    
    
    def change_block(self, telegram_id, new_block):
        """ Функция изменения блока """
        
        self.cursor.execute("UPDATE users SET user_block = %s, last_block_change = %s WHERE telegram_id = %s",
                            (new_block, datetime.now(), telegram_id))
        self.db.commit()
        
        
    def __del__(self):
        """ Закрываем подключение к бд """
        
        self.cursor.close()
        self.db.close()