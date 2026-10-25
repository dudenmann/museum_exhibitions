"""Запуск: python main.py. Даты вводятся в формате ГГГГ-ММ-ДД."""

from datetime import date

from storage import load_museum, save_museum


MENU = """
1 — Залы
2 — Кураторы
3 — Все выставки
4 — Создать выставку
5 — Отменить выставку
6 — Найти свободные залы
7 — Поиск действующих (не отмененных) выставок по названию
8 — Добавить зал
9 — Добавить куратора
0 — Выход
"""


def read_period():
    start = date.fromisoformat(input("Дата начала (ГГГГ-ММ-ДД): "))
    end = date.fromisoformat(input("Дата окончания (ГГГГ-ММ-ДД): "))
    return start, end


def show_halls(halls):
    for hall in halls:
        print(f"{hall.id}: {hall.name} — {hall.capacity} чел., {hall.hall_type}")
    if not halls:
        print("Подходящих залов нет.")


def show_exhibitions(museum, exhibitions):
    for item in exhibitions:
        status = "Отменена" if item.is_cancelled else "Не отменена"
        print(
            f"{item.id}: {item.title} | {item.start_date} — {item.end_date}\n"
            f"  {museum.get_hall(item.hall_id).name}; "
            f"куратор: {museum.get_curator(item.curator_id).name}; {status}"
        )
    if not exhibitions:
        print("Выставок не найдено.")


def execute(museum, choice):
    if choice == "1":
        show_halls(museum.halls)
    elif choice == "2":
        for curator in museum.curators:
            print(f"{curator.id}: {curator.name} — {curator.email}")
    elif choice == "3":
        show_exhibitions(museum, museum.search_exhibitions(include_cancelled=True))
    elif choice == "4":
        title = input("Название: ")
        hall_id = int(input("ID зала: "))
        curator_id = int(input("ID куратора: "))
        start, end = read_period()
        museum.create_exhibition(title, hall_id, curator_id, start, end)
    elif choice == "5":
        museum.cancel_exhibition(int(input("ID выставки: ")))
    elif choice == "6":
        show_halls(museum.available_halls(*read_period()))
    elif choice == "7":
        show_exhibitions(museum, museum.search_exhibitions(input("Название: ")))
    elif choice == "8":
        museum.add_hall(input("Название: "), int(input("Вместимость: ")))
    elif choice == "9":
        museum.add_curator(input("ФИО: "), input("Email: "))
    else:
        raise ValueError("Выберите пункт меню от 0 до 9.")
    return choice in {"4", "5", "8", "9"}


def main():
    print("Сервис учета музейных выставок")
    try:
        museum = load_museum()
    except (OSError, ValueError) as error:
        print(f"Не удалось открыть данные: {error}")
        return 1
    while True:
        try:
            print(MENU)
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return 0
            if execute(museum, choice):
                save_museum(museum)
                print("Изменения сохранены.")
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
            # Не оставляем несохраненные изменения в памяти после ошибки записи.
            try:
                museum = load_museum()
            except (OSError, ValueError) as reload_error:
                print(f"Не удалось восстановить данные: {reload_error}")
                return 1
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
