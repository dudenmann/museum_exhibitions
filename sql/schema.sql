PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS halls (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    capacity INTEGER NOT NULL CHECK(capacity > 0),
    hall_type TEXT NOT NULL,
    description TEXT
);
CREATE TABLE IF NOT EXISTS curators (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    email TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS exhibitions (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    hall_id INTEGER NOT NULL REFERENCES halls(id),
    curator_id INTEGER NOT NULL REFERENCES curators(id),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    description TEXT,
    is_cancelled INTEGER NOT NULL DEFAULT 0 CHECK(is_cancelled IN (0, 1)),
    CHECK(start_date <= end_date)
);
CREATE INDEX IF NOT EXISTS exhibition_hall_dates
    ON exhibitions(hall_id, is_cancelled, start_date, end_date);
CREATE INDEX IF NOT EXISTS exhibition_curator ON exhibitions(curator_id);
CREATE TRIGGER IF NOT EXISTS no_overlap_insert
BEFORE INSERT ON exhibitions WHEN NEW.is_cancelled = 0
BEGIN
    SELECT RAISE(ABORT, 'Зал занят в выбранный период')
    WHERE EXISTS (
        SELECT 1 FROM exhibitions WHERE hall_id = NEW.hall_id
        AND is_cancelled = 0
        AND start_date <= NEW.end_date AND end_date >= NEW.start_date
    );
END;
CREATE TRIGGER IF NOT EXISTS no_overlap_update
BEFORE UPDATE ON exhibitions WHEN NEW.is_cancelled = 0
BEGIN
    SELECT RAISE(ABORT, 'Зал занят в выбранный период')
    WHERE EXISTS (
        SELECT 1 FROM exhibitions WHERE hall_id = NEW.hall_id AND id != NEW.id
        AND is_cancelled = 0
        AND start_date <= NEW.end_date AND end_date >= NEW.start_date
    );
END;
