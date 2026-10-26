# Отчет по практической работе № 7

**Тема:** Основы баз данных и SQL.   
**Дисциплина:** Технологии разработки приложений на базе фреймворков.  
**ФИО студента:** Дудник Валерий Валерьевич  
**Учебная группа:** ЭФБО-08-24
**Индивидуальный проект:** Сервис учета музейных выставок.  
**Ссылка на Git-репозиторий:** 

## 1. Цель работы

Спроектировать реляционное хранилище индивидуального проекта, перенести
данные из JSON в SQLite и использовать SQL-запросы для получения данных
в представлениях Django без перехода на Django ORM.

## 2. Структура базы и перенос данных

Использована шаблонная веб-часть ПР6. Создана база `data/museum.sqlite3`;
схема, ограничения и индексы описаны в `sql/schema.sql`.

| Таблица | Поля и типы |
| --- | --- |
| `halls` | `id INTEGER PK`, `name TEXT`, `capacity INTEGER`, `hall_type TEXT`, `description TEXT` |
| `curators` | `id INTEGER PK`, `name TEXT`, `email TEXT` |
| `exhibitions` | `id INTEGER PK`, `title TEXT`, `hall_id INTEGER FK`, `curator_id INTEGER FK`, `start_date TEXT`, `end_date TEXT`, `description TEXT`, `is_cancelled INTEGER` |

Выставка ссылается на зал и куратора; каждому из них соответствует несколько
выставок. Даты хранятся в ISO-формате, признак отмены — 0/1, описание допускает
NULL. Проверяются положительная вместимость и порядок дат. Индексы помогают
поиску по залу и куратору; триггеры запрещают пересечения выставок.

`db/database.py` открывает соединение, включает `PRAGMA foreign_keys = ON`
и `sqlite3.Row`. `db/import_json.py` загружает и проверяет JSON, создает
таблицы, затем переносит залы, кураторов и выставки через `executemany`
и фиксирует транзакцию. Повторный импорт в заполненную базу отклоняется.
Консольная JSON-версия сохранена, но автоматически с SQLite не синхронизируется.

## 3. SQL и веб-интерфейс

В `sql/queries.sql` реализовано **13 запросов**: два списка, две фильтрации,
два соединения, два агрегатных запроса, две группировки и три дополнительных.
Использованы SELECT, WHERE, JOIN, COUNT/SUM/AVG/MIN/MAX, GROUP BY, HAVING,
ORDER BY, LIMIT/OFFSET, NULL. Пользовательские значения передаются параметрами.

`db/repository.py` выполняет запросы, обращается к полям `Row` по именам,
преобразует даты для шаблонов. Результаты отображаются на `/halls/`,
`/halls/<id>/`, `/halls/available/`, `/exhibitions/`, `/exhibitions/<id>/`,
`/curators/`, `/statistics/` и главной странице. Поиск залов исключает
пересечения с неотмененными выставками, статистика группирует выставки
по залам и кураторам. Навигация и шаблоны ПР6 сохранены; README дополнен.

## 4. Проверка и результат

Команды выполняются из корня проекта с установленными зависимостями:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m flake8 .
```

На этапе ПР7 прошли **32 теста**, check и flake8 — без ошибок. Все
13 запросов выполнены через `python -m db.check_queries`; список таблиц
дополнительно проверен в CLI `python -m sqlite3 data/museum.sqlite3`.
Функция CASEFOLD для поиска по кириллице зарегистрирована в Python-соединении;
в стандартной CLI без регистрации этот дополнительный запрос не выполняется.

На демонстрационных данных: 3 зала, 2 куратора, 4 выставки (1 отменена),
общая вместимость 145. На период 05–10 ноября 2026 года свободен зал № 3.
Количество неотмененных выставок по залам № 1/2/3 — 2/1/0.
Рабочая база также содержит пользовательские записи и может отличаться от demo.

**Git:** коммит `c609c0e`, метка `PR7`, сообщение
`PR7: add SQLite storage, SQL queries and museum statistics`.

## 5. Вывод

Создано реляционное хранилище с ключами и ограничениями. Получена схема
«SQLite → SQL → sqlite3 → context → шаблоны». Фильтрация и подсчеты
перенесены в базу, пользовательские сценарии работают с результатами SQL,
а предыдущая JSON-реализация сохранена для сопоставления.

## Приложение А. Код и перечень запросов

### А.1. Подключение к SQLite

Файл `db/database.py`, состояние `PR7`. Проверка внешних ключей включается
при каждом подключении; `Row` дает доступ к полям по именам.

```python
def get_connection(path=None):
    connection = sqlite3.connect(path or database_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.create_function("CASEFOLD", 1, lambda text: (text or "").casefold())
    return connection
```

### А.2. Поиск свободного зала

Файл `sql/queries.sql`. Параметры — конец искомого периода и его начало.
Отмененные выставки не блокируют пространство.

```sql
-- 04. WHERE и подзапрос: залы без пересечений с периодом (конец, начало).
SELECT * FROM halls
WHERE id NOT IN (
    SELECT hall_id FROM exhibitions WHERE is_cancelled = 0
    AND start_date <= ? AND end_date >= ?
) ORDER BY name, id;
```

### А.3. JOIN, группировка и HAVING

Файл `sql/queries.sql`. Запрос выводит кураторов с числом неотмененных
выставок не меньше переданного порога.

```sql
-- 10. GROUP BY и HAVING: кураторы с заданным минимумом выставок.
SELECT c.id, c.name, COUNT(e.id) AS count
FROM curators c LEFT JOIN exhibitions e
ON e.curator_id = c.id AND e.is_cancelled = 0
GROUP BY c.id, c.name HAVING COUNT(e.id) >= ? ORDER BY count DESC, c.id;
```

### А.4. Полный перечень запросов и использование

| № | Имя запроса | Назначение и место вывода |
| --- | --- | --- |
| 1 | halls_list | Список залов — раздел залов |
| 2 | curators_list | Список кураторов — раздел кураторов |
| 3 | halls_capacity | WHERE по вместимости — фильтр залов |
| 4 | available_halls | WHERE и подзапрос — свободные залы |
| 5 | exhibition_catalog | JOIN, LIMIT/OFFSET — каталог выставок |
| 6 | exhibition_detail | JOIN — карточка выставки |
| 7 | hall_totals | COUNT/SUM/AVG/MIN/MAX — обзор и статистика |
| 8 | exhibition_totals | COUNT/SUM — статистика состояний |
| 9 | exhibitions_by_hall | GROUP BY — число выставок по залам |
| 10 | exhibitions_by_curator | GROUP BY/HAVING — программа кураторов |
| 11 | exhibition_search | LIKE и CASEFOLD — поиск названия |
| 12 | hall_detail | WHERE по ID — карточка зала |
| 13 | missing_descriptions | NULL/пустые значения — полнота описаний |

## Приложение Б. Локальное развертывание по Word-заданию № 7

После SQL-этапа подготовлена итоговая версия `3414d79`: Waitress обслуживает
WSGI на `127.0.0.1:8000`, WhiteNoise отдает собранные статические файлы.
В настройках развертывания `DEBUG=False`, список Host ограничен localhost,
секретный ключ вынесен в локальный файл вне Git. Добавлен журнал запросов
с ротацией, а `/health/` проверяет доступность предметной таблицы базы.

Файл `run_local.py`, итоговая версия:

```python
"""Локальное развертывание: python run_local.py (порт 8000)."""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum_site.deploy")

from waitress import serve  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

if __name__ == "__main__":
    print("Музей: http://127.0.0.1:8000/ (Ctrl+C для остановки)")
    serve(get_wsgi_application(), host="127.0.0.1", port=8000, threads=4)
```

Подготовка и запуск из корня проекта:

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_local
.\.venv\Scripts\python.exe manage.py collectstatic --noinput --settings=museum_site.deploy
.\.venv\Scripts\python.exe -X utf8 run_local.py
```

Выполнен короткий нагрузочный прогон: 100 запросов, 8 параллельных клиентов,
100 успешных ответов; медиана 19,15 мс, p95 559,88 мс. Это локальное измерение,
а не оценка производительности публичного сервера.

`check --deploy` сообщает W004, W008, W011 и W016: HTTPS/HSTS и Secure-cookie
не включены в локальном HTTP-режиме. Системный пользователь, правила
брандмауэра, TLS, автозапуск и внешний мониторинг не настраивались.
Реализован локальный вариант развертывания; невыполненные инфраструктурные
пункты общего Word-задания не заявляются выполненными.

## Приложение В. Материалы к сдаче

- [Демонстрационная SQLite-база без аккаунтов](../docs/submission/pr7-demo.sqlite3).
- [Схема и ограничения](../sql/schema.sql), [SQL-запросы](../sql/queries.sql).
- [Подключение к базе](../db/database.py), [импорт JSON](../db/import_json.py).
- [README проекта](../README.md) и локальный Git с меткой `PR7`.
- [Результаты проверок](../docs/VERIFICATION.md), [данные нагрузочного прогона](../docs/evidence/load-test.json).

Основные требования: «ПР7_Django_SQL.pdf», раздел 5 и пункт 7.5 (с. 48–49).
Дополнение: Word-задание № 7 по развертыванию. Отчет касается индивидуального
проекта; прохождение материалов Яндекс Практикума не заявляется.
Удаленный Git-репозиторий пока не настроен; его адрес заполняется после публикации.
