# Сервис учета музейных выставок

Готовый индивидуальный проект: ПР5 (Django и HTTP), ПР6 (шаблоны),
ПР7 (SQLite и SQL), дополнения из Word (API, роли, безопасность, кэш,
тестирование и локальное развертывание). Упражнения Яндекс Практикума и
«Блогикум» в объем не входят. Отчеты в Markdown: [reports](reports/).

## Открыть сайт

Адрес работающего сервера: http://127.0.0.1:8000/

Для следующего запуска в PowerShell:

```powershell
cd D:\codex-111\museum_exhibitions
.\.venv\Scripts\python.exe -X utf8 run_local.py
```

Окно оставьте открытым; остановка — Ctrl+C. Сервер слушает только localhost.
Не запускайте вторую копию, если порт 8000 уже занят.
Для входа нажмите «Вход для сотрудников». Логин и случайный пароль редактора
находятся в `data/local-access.txt`. Файл исключен из Git: не публикуйте его
и не включайте в отчеты. После входа появляется «Добавить выставку»; там же
можно добавить зал и куратора. Отмена — в карточке выставки.

## Установка с нуля

Фактическая среда: Python 3.12.10, Django 5.2.18. В примере PDF Python 3.11.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m scripts.setup_local
.\.venv\Scripts\python.exe manage.py collectstatic --noinput --settings=museum_site.deploy
.\.venv\Scripts\python.exe -X utf8 run_local.py
```

Setup создает новую базу, учетную запись и секретный ключ, но не заменяет
существующие данные. Импорт берет data/local.json, если он есть, иначе demo.json.
Если файл базы уже существует, но пуст, выполните `python -m db.import_json`.
Для разработки: `python manage.py runserver 127.0.0.1:8000`.
Для демонстрации — run_local.py: Waitress, WhiteNoise, DEBUG=False.
После изменения static повторите collectstatic; после изменения Python —
перезапустите сервер.

## Правила учета

- У выставки один зал и один куратор. Куратор может вести несколько выставок.
- Даты обеих границ включены: после выставки до 10 ноября следующая начинается
  не раньше 11 ноября.
- Пересечения неотмененных выставок в одном зале запрещены, даже при
  одновременных запросах: ограничение дублируется SQLite-триггерами.
- Отмена освобождает зал и сохраняет запись в истории.
- «Не отменена» не означает «проходит сегодня»; есть будущие и прошедшие события.

Демонстрационные данные вымышлены. Рабочие записи пользователя, включая
выставку «Картины», перенесены из JSON без удаления.

## Этапы Git

| Этап | Коммит / тег | Результат |
| --- | --- | --- |
| Подготовка | 953fb6a | Классы, JSON, консоль, 13 тестов |
| ПР5 | a2fe2e7 / PR5 | Django, приложения, URL, view, HTML/CSS, 404 |
| ПР6 | 381dc6d / PR6 | Шаблоны, context, фильтры, static, интерфейс |
| ПР7 | c609c0e / PR7 | SQLite, 13 SQL-запросов, поиск, статистика |
| Дополнения Word | текущая версия | API, учетные записи, кэш, локальный сервер |

Посмотреть код этапа без переключения рабочей папки:
`git show PR5:halls/views.py`, `git show PR6:templates/base.html`.

## Где что находится

| Файл или папка | Назначение |
| --- | --- |
| models.py, services.py, storage.py, main.py | Сохраненная консольная JSON-версия |
| museum_site/ | Настройки, общие URL, WSGI, локальное развертывание |
| homepage/, halls/, exhibitions/ | Представления страниц и шаблоны приложений |
| templates/base.html, templates/includes/ | Общий макет, навигация, карточки |
| static/ | Собственные CSS, SVG-логотип, JavaScript |
| sql/schema.sql | Предметные таблицы, ключи, индексы, триггеры |
| sql/queries.sql | 13 запросов, используемых сайтом |
| db/database.py, db/repository.py | sqlite3, Row, выполнение SQL |
| db/import_json.py, db/mutations.py | Импорт и изменение записей |
| db/statistics.py | Кэш сводки на 30 секунд |
| accounts/, api/ | Вход, роли и REST API |
| data/museum.sqlite3 | Рабочая база с локальными учетными записями |
| docs/ | API, памятка по практикам, результаты проверок |

## База данных

halls: id INTEGER PK, name TEXT, capacity INTEGER, hall_type TEXT, description TEXT.
curators: id INTEGER PK, name TEXT, email TEXT.
exhibitions: id INTEGER PK, title TEXT, hall_id INTEGER FK, curator_id INTEGER FK,
start_date TEXT, end_date TEXT, description TEXT, is_cancelled INTEGER (0/1).
Даты хранятся как ГГГГ-ММ-ДД, description допускает NULL.
Дополнительная accounts содержит username, password_hash, role (viewer/editor).
Django ORM не используется, включая учетные записи.

В каждом соединении включен PRAGMA foreign_keys=ON; значения передаются
параметрами. Запросы: 2 списка, 2 фильтрации, 2 JOIN, 2 агрегатных,
2 группировки, поиск, карточка и NULL. Используются HAVING, MIN/MAX/AVG/SUM/COUNT,
ORDER BY, LIMIT/OFFSET. CASEFOLD регистрируется в Python для поиска по кириллице.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m db.check_queries
.\.venv\Scripts\python.exe -X utf8 -m sqlite3 data\museum.sqlite3
```

Вторая команда — SQLite CLI Python 3.12. Пример запроса:
`SELECT name, capacity FROM halls ORDER BY capacity DESC;`
CASEFOLD работает в check_queries, но не зарегистрирован в обычной CLI.
Импорт: `python -m db.import_json`. Повторный импорт в заполненную базу
отклоняется. JSON и консоль (python main.py) теперь отдельная предыдущая версия:
они не синхронизируются автоматически с SQLite. Для сайта источник данных — БД.

## Проверки и материалы

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m flake8 .
.\.venv\Scripts\python.exe -m scripts.load_test
```

Тесты используют отдельные временные базы. Нагрузочная проверка требует
запущенного сайта. Результаты: docs/VERIFICATION.md.
Памятка к защите: docs/PRACTICES.md. API: docs/API.md.
Развертывание: docs/DEPLOYMENT.md.
Для приложения к ПР7: docs/submission/pr7-demo.sqlite3 — только предметные
таблицы и demo-данные, без аккаунтов и пользовательских секретов.
