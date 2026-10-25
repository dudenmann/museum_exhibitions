"""Сценарии учета: один и тот же код можно вызывать из консоли и веба."""

from dataclasses import replace
from datetime import date

from models import Curator, Exhibition, Hall


class Museum:
    def __init__(self, halls=(), curators=(), exhibitions=()):
        self.halls = list(halls)
        self.curators = list(curators)
        self.exhibitions = list(exhibitions)
        self.validate()

    def validate(self):
        for collection in (self.halls, self.curators, self.exhibitions):
            ids = [item.id for item in collection]
            if len(ids) != len(set(ids)):
                raise ValueError("Обнаружены повторяющиеся идентификаторы.")
        for item in self.exhibitions:
            self.get_hall(item.hall_id)
            self.get_curator(item.curator_id)
            for other in self.exhibitions:
                if (
                    item.id != other.id
                    and item.hall_id == other.hall_id
                    and not item.is_cancelled
                    and other.overlaps(item.start_date, item.end_date)
                ):
                    raise ValueError("В одном зале пересекаются даты выставок.")

    @staticmethod
    def _find(collection, item_id, label):
        for item in collection:
            if item.id == item_id:
                return item
        raise ValueError(f"{label} с ID {item_id} не найден(а).")

    @staticmethod
    def _next_id(collection):
        return max((item.id for item in collection), default=0) + 1

    def get_hall(self, hall_id):
        return self._find(self.halls, hall_id, "Зал")

    def get_curator(self, curator_id):
        return self._find(self.curators, curator_id, "Куратор")

    def get_exhibition(self, exhibition_id):
        return self._find(self.exhibitions, exhibition_id, "Выставка")

    def add_hall(self, name, capacity, hall_type="Универсальный", description=""):
        item = Hall(self._next_id(self.halls), name, capacity, hall_type, description)
        self.halls.append(item)
        return item

    def add_curator(self, name, email):
        item = Curator(self._next_id(self.curators), name, email)
        self.curators.append(item)
        return item

    def available_halls(self, start: date, end: date):
        if start > end:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
        occupied = {
            item.hall_id for item in self.exhibitions if item.overlaps(start, end)
        }
        return [hall for hall in self.halls if hall.id not in occupied]

    def create_exhibition(self, title, hall_id, curator_id, start, end, description=""):
        self.get_hall(hall_id)
        self.get_curator(curator_id)
        available = {hall.id for hall in self.available_halls(start, end)}
        if hall_id not in available:
            raise ValueError("Зал занят в выбранный период.")
        item = Exhibition(
            self._next_id(self.exhibitions), title, hall_id, curator_id,
            start, end, description,
        )
        self.exhibitions.append(item)
        return item

    def cancel_exhibition(self, exhibition_id):
        item = self.get_exhibition(exhibition_id)
        cancelled = replace(item, is_cancelled=True)
        self.exhibitions[self.exhibitions.index(item)] = cancelled
        return cancelled

    def search_exhibitions(self, query="", include_cancelled=False):
        return sorted(
            (
                item for item in self.exhibitions
                if query.casefold() in item.title.casefold()
                and (include_cancelled or not item.is_cancelled)
            ),
            key=lambda item: (item.start_date, item.id),
        )
