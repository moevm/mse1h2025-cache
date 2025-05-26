# Использование Testcontainers с MongoDB в Python

## Введение

Testcontainers — это библиотека для тестирования, которая предоставляет простые и легковесные API для настройки интеграционных тестов с использованием реальных сервисов, запущенных в Docker-контейнерах.
С помощью Testcontainers можно писать тесты, которые взаимодействуют с теми же сервисами, что и в production, без необходимости использования моков или in-memory сервисов.
Рассмотрим, как использовать Testcontainers с Python для тестирования приложения, работающего с MongoDB.

## Установка необходимых пакетов

Для работы с Testcontainers и MongoDB установим необходимые зависимости:

```sh
pip install testcontainers pymongo pytest
```

## Testcontainers Core

`testcontainers-core` — это основная библиотека для запуска Docker-контейнеров в тестовой среде.

### `DockerContainer`

Класс `DockerContainer` используется для создания и управления контейнерами.
```python
class DockerContainer(image: str, docker_client_kw: dict | None = None, **kwargs)
```
```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

with DockerContainer("hello-world") as container:
   delay = wait_for_logs(container, "Hello from Docker!")
```

### `DockerImage`

Класс `DockerImage` используется для сборки образов Docker.
```python
class DockerImage(path: str | PathLike, docker_client_kw: dict | None = None, tag: str | None = None, clean_up: bool = True, dockerfile_path: str | PathLike = 'Dockerfile', no_cache: bool = False, **kwargs)
```
```python
from testcontainers.core.image import DockerImage

with DockerImage(path="./core/tests/image_fixtures/sample/", tag="test-image") as image:
   logs = image.get_logs()
```

### Параметры:
- **`tag`** – Тег создаваемого образа (по умолчанию `None`).
- **`path`** – Путь к контексту сборки.
- **`dockerfile_path`** – Путь к Dockerfile (по умолчанию `Dockerfile`).
- **`no_cache`** – Отключение кэширования при сборке.

### Пример использования `DockerContainer` и `DockerImage` для создания контейнера:

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.image import DockerImage

with DockerImage(path="./core/tests/image_fixtures/sample/", tag="test-sample:latest") as image:
    with DockerContainer(str(image)) as container:
        delay = wait_for_logs(container, "Test Sample Image")
```

## Создание теста с использованием Testcontainers и MongoDB

Рассмотрим простой тест, который запускает MongoDB в контейнере, подключается к ней и выполняет базовые операции.

```python
from testcontainers.mongodb import MongoDbContainer
from pymongo import MongoClient
import pytest

def test_mongodb_container():
    # Запуск контейнера с MongoDB
    with MongoDbContainer("mongo:latest") as mongo:
        # Получаем URL для подключения к MongoDB
        mongo_url = mongo.get_connection_url()

        # Подключаемся к MongoDB
        client = MongoClient(mongo_url)
        db = client.test_database
        collection = db.test_collection

        # Вставляем документ в коллекцию
        document = {"name": "Test", "value": 123}
        collection.insert_one(document)

        # Проверяем, что документ был добавлен
        result = collection.find_one({"name": "Test"})
        assert result is not None
        assert result["value"] == 123

        # Удаляем документ
        collection.delete_one({"name": "Test"})

        # Проверяем, что документ был удален
        result = collection.find_one({"name": "Test"})
        assert result is None
```

## Описание параметров `MongoDbContainer`

Класс `MongoDbContainer` позволяет запускать контейнер с MongoDB и предоставляет методы для работы с ним.

```python
class MongoDbContainer(
    image: str = "mongo:latest", 
    port: int = 27017, 
    username: str | None = None, 
    password: str | None = None, 
    dbname: str | None = None, 
    **kwargs
)
```

### Основные параметры:

- **`image`** — образ Docker-контейнера с MongoDB (по умолчанию `mongo:latest`);
- **`port`** — порт, используемый для подключения к MongoDB (по умолчанию `27017`);
- **`username`, `password`** — учетные данные для аутентификации (необязательные);
- **`dbname`** — имя базы данных (необязательный параметр);
- **`**kwargs`** — дополнительные параметры, передаваемые в контейнер.

## Запуск тестов

Запустим тест с помощью `pytest`:

```sh
pytest test_mongodb.py
```

Где `test_mongodb.py` — это файл, содержащий тест `test_mongodb_container`.

## Заключение

Testcontainers — это удобный инструмент для написания интеграционных тестов, использующих реальные сервисы в Docker-контейнерах. 
В данном туториале мы рассмотрели, как использовать Testcontainers для тестирования MongoDB в Python. 
С его помощью можно легко и быстро настраивать окружение для тестов без необходимости устанавливать MongoDB вручную.

