# kasperdb

**kasperdb** (пакет `kasdb`) — это упрощённая локальная база данных для Python, предназначенная для быстрого хранения и управления данными непосредственно на диске без необходимости использования сторонних серверов или сложных конфигураций. Библиотека поддерживает два формата хранения: JSON (для функций верхнего уровня `create/get/set/delete`) и MessagePack (для объектно-ориентированных классов `DB` и `AsyncDB`). Проект написан на Python и зависит от пакетов `msgpack` и `colorama`.

Библиотека предоставляет два подхода к работе с данными: процедурный API на основе файлов JSON и объектно-ориентированный API на основе файлов `.db` (MessagePack). Дополнительно доступен асинхронный класс `AsyncDB` для использования в проектах на `asyncio`. Опциональный режим отладки выводит цветные сообщения в консоль при каждой операции с базой данных.

---

## Установка

```bash
pip install kasdb
```

---

## config.debug — включение режима отладки

Глобальный флаг `debug` в модуле `kasdb.config` управляет выводом цветных лог-сообщений в консоль при каждой операции. По умолчанию отладка отключена (`False`).

```python
import kasdb.config as config

# Включить отладочные сообщения (зелёный — успех, жёлтый — предупреждение, красный — ошибка)
config.debug = True

# Отключить отладочные сообщения
config.debug = False
```

---

## create — создание базы данных

Создаёт новый JSON-файл базы данных с указанными начальными ключами, значения которых устанавливаются в `None`. Если файл уже существует, повторное создание игнорируется.

```python
from kasdb import create
import kasdb.config as config

config.debug = True

# Создать базу данных "users" с ключами "name", "age", "email"
create("users", ["name", "age", "email"])
# Вывод: база данных users создана с такими данными: {'name': None, 'age': None, 'email': None}

# Повторный вызов — создание игнорируется, файл уже существует
create("users", ["name", "age", "email"])
```

---

## get — получение данных из базы

Читает данные из JSON-файла базы данных. Можно получить все данные целиком или значение конкретного ключа.

```python
from kasdb import create, get, set
import kasdb.config as config

config.debug = True

create("products", ["title", "price", "stock"])
set("products", "Ноутбук", "title")
set("products", 59999, "price")
set("products", 10, "stock")

# Получить все данные
all_data = get("products")
print(all_data)
# {'title': 'Ноутбук', 'price': 59999, 'stock': 10}

# Получить значение конкретного ключа
price = get("products", "price")
print(price)
# 59999

# Получить несуществующий ключ — вывод ошибки в консоль
get("products", "nonexistent_key")
# [RED] базы данных products не существует или же ключ nonexistent_key ненайден
```

---

## set — запись и обновление данных

Записывает новые данные в базу. Если указан ключ — обновляет только его значение; если ключ не указан — перезаписывает всё содержимое базы целиком.

```python
from kasdb import create, get, set
import kasdb.config as config

config.debug = True

create("settings", ["theme", "language", "volume"])

# Обновить конкретный ключ
set("settings", "dark", "theme")
# Вывод: данные успешно обновлены

set("settings", "ru", "language")
set("settings", 80, "volume")

print(get("settings"))
# {'theme': 'dark', 'language': 'ru', 'volume': 80}

# Перезаписать всю базу целиком
set("settings", {"theme": "light", "language": "en", "volume": 50})
print(get("settings"))
# {'theme': 'light', 'language': 'en', 'volume': 50}
```

---

## delete — удаление базы данных

Полностью удаляет файл базы данных с диска. При попытке удалить несуществующую базу выводится сообщение об ошибке.

```python
from kasdb import create, delete
import kasdb.config as config

config.debug = True

create("temp", ["x", "y"])

# Удалить базу данных
delete("temp")
# Вывод: база данных temp успешно удалена

# Попытка удалить несуществующую базу
delete("temp")
# [RED] базы данных temp не существует
```

---

## if_get — условное получение данных

Возвращает данные из базы только если выполняется переданное условие (`condition=True`). Если условие ложно — данные не возвращаются.

```python
from kasdb import create, set, if_get
import kasdb.config as config

config.debug = True

create("session", ["user_id", "token", "is_admin"])
set("session", 42, "user_id")
set("session", "abc123", "token")
set("session", True, "is_admin")

is_admin = if_get("session", "is_admin")

# Получить все данные только если пользователь — администратор
if is_admin:
    data = if_get("session", condition=True)
    print(data)
    # {'user_id': 42, 'token': 'abc123', 'is_admin': True}

# Получить конкретный ключ по условию
token = if_get("session", condition=True, key="token")
print(token)
# abc123

# Условие не выполнено
result = if_get("session", condition=False)
# Вывод: условие не выполнено данные не получены
# result = None
```

---

## where_get — получение данных с проверкой вхождения

Возвращает значение ключа из базы данных только если в нём содержится указанная подстрока или элемент (`where`). Полезно для поиска по строковым значениям.

```python
from kasdb import create, set, where_get
import kasdb.config as config

config.debug = True

create("article", ["title", "tags", "author"])
set("article", "Введение в Python", "title")
set("article", "python,tutorial,beginner", "tags")

# Найти данные, если ключ "tags" содержит "python"
result = where_get("article", "tags", "python")
print(result)
# python,tutorial,beginner
# Вывод: получины данные с условием

# Условие не выполнено — подстрока не найдена
result = where_get("article", "tags", "javascript")
# Вывод: условие не выполнено данные не получены
# result = None
```

---

## DB — объектно-ориентированная база данных (MessagePack)

Класс `DB` предоставляет синхронный интерфейс для хранения данных в бинарном формате MessagePack (файл `.db`). Поддерживает события `getData` и `saveData` для отслеживания операций.

```python
from kasdb import DB

# Создать базу данных с начальными данными
db = DB("myapp", extension=".db", data={"users": [], "count": 0})

# Сохранить данные
db.saveData("users", [{"id": 1, "name": "Алексей"}, {"id": 2, "name": "Мария"}])
db.saveData("count", 2)

# Получить все данные
all_data = db.getData()
print(all_data)
# {'users': [{'id': 1, 'name': 'Алексей'}, {'id': 2, 'name': 'Мария'}], 'count': 2}

# Получить данные по ключу
users = db.getData("users")
print(users)
# [{'id': 1, 'name': 'Алексей'}, {'id': 2, 'name': 'Мария'}]

# Подписаться на события
def on_save(event):
    print(f"Сохранено: ключ={event['key']}, значение={event['value']}")

def on_get(event):
    print(f"Получено: ключ={event['key']}, файл={event['filename']}")

db.on("saveData", on_save)
db.on("getData", on_get)

db.saveData("count", 3)
# Сохранено: ключ=count, значение=3

db.getData("count")
# Получено: ключ=count, файл=myapp.db
```

---

## AsyncDB — асинхронная база данных (MessagePack)

Класс `AsyncDB` предоставляет асинхронный интерфейс на базе `asyncio` и MessagePack. Методы `getData` и `saveData` являются корутинами и должны вызываться через `await`. Ввод-вывод выполняется в отдельном потоке через `run_in_executor`.

```python
import asyncio
from kasdb import AsyncDB

async def main():
    # Создать асинхронную базу данных с начальными данными
    db = AsyncDB("async_store", extension=".db", data={"tasks": [], "done": 0})

    # Подписаться на события
    def on_save(event):
        print(f"[AsyncDB] Сохранено: {event['key']} = {event['value']}")

    db.on("saveData", on_save)

    # Сохранить данные асинхронно
    await db.saveData("tasks", ["задача 1", "задача 2", "задача 3"])
    await db.saveData("done", 1)

    # Получить все данные
    all_data = await db.getData()
    print(all_data)
    # {'tasks': ['задача 1', 'задача 2', 'задача 3'], 'done': 1}

    # Получить конкретный ключ
    tasks = await db.getData("tasks")
    print(tasks)
    # ['задача 1', 'задача 2', 'задача 3']

asyncio.run(main())
```

Библиотека легко интегрируется в любой проект: достаточно импортировать нужные функции или классы из пакета `kasdb`. Класс `AsyncDB` обеспечивает неблокирующую работу с файлами в асинхронных приложениях на базе `asyncio` (например, в Telegram-ботах или веб-серверах). Механизм событий (`on("getData")`, `on("saveData")`) позволяет добавлять логирование или побочные эффекты без изменения основной логики приложения.
