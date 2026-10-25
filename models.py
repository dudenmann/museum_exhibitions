"""Предметные сущности. Не зависят от консоли или будущего Django."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Hall:
    id: int
    name: str
    capacity: int
    hall_type: str = "Универсальный"
    description: str = ""

    def __post_init__(self):
        if self.id <= 0 or not self.name.strip() or self.capacity <= 0:
            raise ValueError("Залу нужны положительный ID, название и вместимость.")


@dataclass(frozen=True)
class Curator:
    id: int
    name: str
    email: str

    def __post_init__(self):
        if self.id <= 0 or not self.name.strip() or "@" not in self.email:
            raise ValueError("Куратору нужны положительный ID, ФИО и email с @.")


@dataclass(frozen=True)
class Exhibition:
    id: int
    title: str
    hall_id: int
    curator_id: int
    start_date: date
    end_date: date
    description: str = ""
    is_cancelled: bool = False

    def __post_init__(self):
        if min(self.id, self.hall_id, self.curator_id) <= 0 or not self.title.strip():
            raise ValueError("Выставке нужны положительные ID и название.")
        if self.start_date > self.end_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")

    def overlaps(self, start: date, end: date) -> bool:
        """Обе граничные даты включены в период проведения."""
        return (
            not self.is_cancelled
            and self.start_date <= end
            and start <= self.end_date
        )
