# Юнит-тестирование. Моковое тестирование

## Суть юнит-тестирования

Суть юнит-тестирования состоит в тестировании конкретных единиц приложения, например, отдельно взятых классов. То есть
идеальный юнит-тест должен тестировать поведение непосредственно тестируемого класса.  
Например, тестируется класс, который считает стоимость товара с учетом НДС. НДС получается через другой класс,
отвечающий за получение НДС (например, запрос к API). Пишется базовый тест, что стоимость товара за 100р должна
подняться до 120р. На первый взгляд, всё хорошо - тест проходит. Но в какой-то момент НДС изменяется и тест начинает
падать, хотя логика работы класса абсолютно верная.

## Предпосылки мокового тестирования

Данная ошибка произошла из-за того, что мы тестировали не 1, а 2 класса, причем первый зависел от второго. Поэтому
изменение логики 2-го класса привело к "нарушению" логики 1-го.  
Ситуация может ухудшиться, если класс A зависит от класса B, который зависит от класса C и так далее до Z. То есть если
какой-то разработчик "сломает" класс Z, то за ним полетят все тесты вплоть до A, хотя изначально проблема крылась в Z.
Также отлов подобных ошибок может занять очень много времени, поскольку проблема будет искаться не в Z, а в A.
Для избежания подобных проблем можно заменить класс B заглушкой или моком.  
Подробнее можно посмотреть [тут](https://youtu.be/61duchvKI6o?t=774).

## Когда применять моки

* Многоуровневая зависимость
* Сложность инициализации класса (например, класс ходит в БД, которую не хочется поднимать для тестов)
* Тестирование контроллеров, клиентов. То есть классов, так или иначе ходящих в сеть и ожидающих ответа со стороны

## Чем отличается паттерн Mock от паттерна Stub

Mock - в переводе "дразнить". Другими словами, это класс, копирующий сигнатуры методов мокируемого класса, то есть для
внешних классов он ничем не отличается от оригинала. Но при этом моковый класс дает возможность на лету переопределять
поведение методов.  
В то же время Stub - заглушка. Концептуально он не отличается от мока, поскольку он является наследником мокируемого
класса, то есть так же неотличим от него. Но при этом его поведение определяется не в рантайме, а на этапе написания
кода. Примером может служить реализация In-Memory репозитория взамен настоящего, ходящего в БД.  
Оба паттерна имеют место в определенных ситуациях, но стоит учитывать, что моки больше нагружают тесты, поскольку
определяются в рантайме, а также требуют большего количества манипуляций (вместо того, чтобы один раз написать Stub,
приходится много раз переопределять различные методы в зависимости от теста). Поэтому моки необходимо применять в случае
крайней необходимости или ненадобности мокировать целый класс, а единичный метод для ускорения написания теста. Также
они могут пригодиться для перехвата вызовов класса (Spy).

## Реализация Mock в Python

Реализацией Mock в Python является библиотека [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/).

### Установка

`pip install pytest-mock`

### Использование в тестах

Данный тест проверяет, что был вызван метод `os.remove` с аргументом `file`. Для этого создается `@pytest.fixture` с
перехватом метода.

```python
import os
import pytest

from unittest.mock import MagicMock
from pytest_mock import MockerFixture


class UnixFS:

    @staticmethod
    def rm(filename):
        os.remove(filename)


@pytest.fixture(name="func")
def fixture_func(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("os.remove", autospec=True)


def test_unix_fs(func: MagicMock):
    UnixFS.rm('file')
    func.assert_called_once_with('file')
```

### Функционал

`MockerFixture` предоставляет следующий функционал:

* `mocker.patch` - Патч функции или метода
* `mocker.patch.object` - Патч метода конкретного объекта
* `mocker.patch.multiple` - Патч нескольких функций или методов
* `mocker.patch.dict` - Патч словаря
* `mocker.patch.stopall` - Снятие всех патчей
* `mocker.patch.stop` - Снятие определенного патча

Например, `mocker.patch("mock_examples.area.PI", 3.0)` позволит изменить константу в файле _mock_examples/area.py_ на 3

### Примеры использования

```python
import math
import pytest

from unittest.mock import MagicMock
from pytest_mock import MockerFixture


def calculate_sqrt(value):
    return math.sqrt(value)


@pytest.fixture
def sqrt_mocker(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('math.sqrt', return_value=4.0)


def test_calculate_sqrt(sqrt_mocker: MagicMock):
    result = calculate_sqrt(16)

    sqrt_mocker.assert_called_once_with(16)

    assert result == 4.0
```

```python
import pytest

from unittest.mock import MagicMock
from pytest_mock import MockerFixture


def get_current_time():
    import time
    return time.time()


@pytest.fixture
def time_mocker(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('time.time', return_value=1234567890.0)


def test_get_current_time(time_mocker: MagicMock):
    result = get_current_time()
    
    time_mocker.assert_called_once()

    assert result == 1234567890.0
```

```python
import pytest

from unittest.mock import MagicMock
from pytest_mock import MockerFixture


def divide(a, b):
    return a / b


@pytest.fixture
def divide_mocker(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(f'{__name__}.divide', side_effect=ZeroDivisionError("division by zero"))


def test_divide_by_zero(divide_mocker: MagicMock):
    with pytest.raises(ZeroDivisionError) as exc_info:
        divide(10, 0)

    divide_mocker.assert_called_once()

    assert str(exc_info.value) == "division by zero"
```