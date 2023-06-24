#from django.test import TestCase

# Create your tests here.
from requests import head
import time
import threading
# Импорт модуля psycopg2 в программу
import psycopg2
# Импорт модуля pymssql в программу
import pymssql
# Импорт модуля pyodbc в программу
import pyodbc


# Cоединение с базой данных
# postgres
#CS = psycopg2.connect("postgres://htfurnveuhauhq:385ae46a03b26021a27c086b1ebe8009638fff6a7f630190c0d0da7d4c2bb1d9@ec2-44-209-57-4.compute-1.amazonaws.com:5432/d9kloeuv0t5ghq", sslmode="require")
#CS = psycopg2.connect(user="customer", password="customer", host="127.0.0.1", port="5432", database="price")

# mssql
server = 'bestpricetest.mssql.somee.com' 
database = 'bestpricetest' 
username = 'bestpricetest_SQLLogin_1' 
password = 'rs356opflg' 
CS = pymssql.connect(server, username, password, database)
#server = r'.\SQLEXPRESS' 
#database = r'Price' 
#username = r'DESKTOP-UEIJEC8' 
#password = r'3552998' 
#CS = pymssql.connect(server, username, password, database)

# odbc
#server = 'bestpricetest.mssql.somee.com' 
#database = 'bestpricetest' 
#username = 'bestpricetest_SQLLogin_1' 
#password = 'rs356opflg' 
#CS = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password)



# Запрос SQL
SQL = "SELECT * FROM prices"

# Базовый адрес веб-сервера
BASE_URL = "http://127.0.0.1:8000/api/prices/"
#BASE_URL = "http://127.0.0.1:8000/index"
#BASE_URL = 'https://bestpricetest.herokuapp.com/index'

# Количество повторений для запроса в потоке
AMOUNT = 1

##### Главная программа #####
def main():
    print("Проверка прямого запроса к базе данных")
    consistent_work1()
    work_in_the_flow1()
    print("Количество повторений для запроса в потоке", AMOUNT)
    #print("Проверка запросов к веб-серверу")
    #consistent_work2()
    #work_in_the_flow2()
    #print("Количество повторений для запроса в потоке", AMOUNT)

##### Проверка прямого запроса к базе данных #####
# Проверка последовательного обращения к базе данных
def consistent_work1():
    try:
        # Время старта
        start = time.time()
        # Подключение к PostgreSQL
        conn = CS
        # Объект cursor, позволяет взаимодействовать с базой данных 
        cursor = conn.cursor()
        for i in range(AMOUNT):
            # С помощью метода execute объекта cursor можно выполнить запрос в базу данных из Python.
            # Он принимает SQL-запрос в качестве параметра и возвращает resultSet (строки базы данных):
            cursor.execute(SQL)
            result = cursor.fetchall()
            #for row in result:
            #    print(row[0], row[1], row[2], row[3], row[4])
            # Количество записей
            #print(len(result))
        print(f'Время, затраченное при последовательном обращении: {time.time() - start : .2f} seconds')
    except Exception as exception:
        print(exception)

# Функция выполняющая запрос к базе данных в потоке
def thread_function(cursor):
    try:
        # С помощью метода execute объекта cursor можно выполнить запрос в базу данных из Python.
        # Он принимает SQL-запрос в качестве параметра и возвращает resultSet (строки базы данных):
        cursor.execute(SQL)
        result = cursor.fetchall()
        #for row in result:
        #    print(row[0], row[1], row[2], row[3], row[4])
        # Количество записей
        #print(len(result))
    except Exception as exception:
        print(exception)

# Проверка в потоке
def work_in_the_flow1():
    try:
        # Время старта
        start = time.time()
        # Подключение к PostgreSQL
        conn = CS
        # Объект cursor, позволяет взаимодействовать с базой данных 
        cursor = conn.cursor()
        # Список потоков
        threads = []
        for i in range(AMOUNT):
            # Создание потока
            thread = threading.Thread(target=thread_function, args=(cursor,))
            # Добавить поток в список
            threads.append(thread)
            # Запуск потока
            thread.start()
        for thread in threads:
            # Указать одному потоку дождаться завершения потока
            thread.join()        
        print(f'Время, затраченное в потоке: {time.time() - start : .2f} seconds')
    except Exception as exception:
        print(exception)
        
##### Проверка запросов к веб-серверу #####
    
# Проверка последовательного обращения к веб-серверу
def consistent_work2():
    try:
        # Время старта
        start = time.time()
        for i in range(AMOUNT):
            response = head(BASE_URL)
            #response = head('BASE_URL')
        print(f'Время, затраченное при последовательном обращении: {time.time() - start : .2f} seconds')
    except Exception as exception:
        print(exception)

# Проверка в потоке
def work_in_the_flow2():
    try:
        # Время старта
        start = time.time()
        # Список потоков
        threads = []
        for i in range(AMOUNT):
            # Создание потока
            thread = threading.Thread(target=head, args=(BASE_URL,))
            # Добавить поток в список
            threads.append(thread)
            # Запуск потока
            thread.start()
        for thread in threads:
            # Указать одному потоку дождаться завершения потока
            thread.join()
        print(f'Время, затраченное в потоке: {time.time() - start : .2f} seconds')
    except Exception as exception:
        print(exception)

##### Вызов функции main #####
main()
