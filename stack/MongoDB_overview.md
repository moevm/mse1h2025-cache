## Причиниы выбора в качестве базы данных MongoDB:

- достаточность функционала
- удобство в использовании
- возможность хранить данные в формате json документов
- отсутствие сложных связей в данных

## Обзор общего функционала базы данных (на примере python):

- импортирование библиотеки
```python
from pymongo import MongoClient
```
- подключение к сессии
```python
client = MongoClient("mongodb://localhost:27017/")
# Проверяем список доступных баз данных
print(client.list_database_names())
```
- выбор коллекций
```python
# Выбираем (или создаем, если не существует) базу данных "mydatabase"
db = client["mydatabase"]
# Выбираем (или создаем) коллекцию "users"
collection = db["users"]
# Проверяем существующие коллекции
print(db.list_collection_names())
```
- добавление документов в базу данных
```python
user = {
    "name": "Alice",
    "age": 25,
    "email": "alice@example.com"
}
# Вставляем документ в коллекцию
insert_result = collection.insert_one(user)
# Получаем ID вставленного документа
print(f"Inserted document ID: {insert_result.inserted_id}")

users = [
    {"name": "Bob", "age": 30, "email": "bob@example.com"},
    {"name": "Charlie", "age": 35, "email": "charlie@example.com"},
]

insert_many_result = collection.insert_many(users)

# Получаем список вставленных ID
print(insert_many_result.inserted_ids)
```
- получение документов из базы данных с использованием фильтрации
```python
# поиск одно документа
user = collection.find_one({"name": "Alice"})
print(user)

# получение всех документов
all_users = collection.find()
for user in all_users:
    print(user)

# фильтрация
# Поиск всех пользователей старше 30 лет
filtered_users = collection.find({"age": {"$gt": 30}})
for user in filtered_users:
    print(user)

# получение отдельных полей
# Получаем только имена всех пользователей
users_projection = collection.find({}, {"name": 1, "_id": 0})
for user in users_projection:
    print(user)
```
- обновление записей
```python
# обновление одного документа
collection.update_one({"name": "Alice"}, {"$set": {"age": 26}})
# обновление нескольких документов
collection.update_many({"age": {"$gt": 30}}, {"$set": {"status": "senior"}})
```
- удаление записей
```python
# удаление одного документа
collection.delete_one({"name": "Charlie"})
# удаление документов с фильтрацией
collection.delete_many({"age": {"$gt": 30}})
```
- возможность использования индексов
```python
collection.create_index("email", unique=True)
print(collection.index_information())
```
- закрытие соединения (либо сессия закрывается при завершении скрипта)
```python
client.close()
```


## Так же предложен пример реализация времени жизни для документов (данные в формате pandas.DataFrame)
```python
import pandas as pd
from pymongo import MongoClient, ASCENDING
from datetime import datetime


# Создание DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)

# Подключение к MongoDB и создание коллекции
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['mycollection']

# Сериализация и сохранение в MongoDB с временем создания
df['createdAt'] = datetime.now()  # Добавляем поле с текущей датой
collection.insert_many(df.to_dict(orient='records'))

# Создание TTL индекса на поле createdAt
collection.create_index([("createdAt", ASCENDING)], expireAfterSeconds=86400)  # 86400 секунд = 24 часа

# Извлечение данных из MongoDB
result = collection.find()
data_from_mongo = list(result)

# Преобразование обратно в DataFrame
df_from_mongo = pd.DataFrame(data_from_mongo)

# Очистка данных
df_from_mongo = df_from_mongo.drop(columns='_id')  # Удаляем поле _id

# Проверка
print(df_from_mongo)
```


## Запуск базы данных (на примере docker-compose):

самый базвый вариант файла docker-compose.yml:
```yaml
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb_container
    restart: always
    ports:
      - "27017:27017"

volumes:
  mongo_data:
```
В этом файле создаётся стандартный контейнер с базой данных MongoDB. Доступ к запущеной базе данных предоставляется по порту 27017. Так же задаётся место, где будут храниться данные - для этого указан том volumes, данные будут храниться в специальной дирректории внутри Docker. Данные возможно будет восстановить после остановки или удаления контейнера.

Для запуска контейнера:
```shell
docker compose up -d
```
Для остановки контейнера:
```shell
docker compose down
```
Найти данные можно внутри docker volumes:
```shell
docker volume ls
```
Пример вывода:
```shell
DRIVER    VOLUME NAME
local     mongo_data
```
Посмотреть путь к данным:
```shell
docker volume inspect mongo_data
```
Пример вывода:
```json
[
    {
        "CreatedAt": "2024-06-01T12:00:00Z",
        "Mountpoint": "/var/lib/docker/volumes/mongo_data/_data",
        "Name": "mongo_data",
        "Driver": "local"
    }
]
```
Получить доступ к данным внутри контейнера:
```shell
docker exec -it mongodb_container bash
```
Затем внутри контейнера:
```shell
ls /data/db
```
