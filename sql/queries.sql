-- name: halls_list
-- 01. Список залов; используется на странице залов.
SELECT * FROM halls ORDER BY name, id;

-- name: curators_list
-- 02. Список кураторов; используется на странице кураторов.
SELECT * FROM curators ORDER BY name, id;

-- name: halls_capacity
-- 03. WHERE: залы нужной вместимости.
SELECT * FROM halls WHERE capacity >= ? ORDER BY capacity, id;

-- name: available_halls
-- 04. WHERE и подзапрос: залы без пересечений с периодом (конец, начало).
SELECT * FROM halls
WHERE id NOT IN (
    SELECT hall_id FROM exhibitions WHERE is_cancelled = 0
    AND start_date <= ? AND end_date >= ?
) ORDER BY name, id;

-- name: exhibition_catalog
-- 05. JOIN: каталог выставок с названием зала и куратором, постраничная выборка.
SELECT e.*, h.name AS hall_name, c.name AS curator_name
FROM exhibitions e JOIN halls h ON h.id = e.hall_id
JOIN curators c ON c.id = e.curator_id
ORDER BY e.start_date, e.id LIMIT ? OFFSET ?;

-- name: exhibition_detail
-- 06. JOIN: полная карточка выбранной выставки.
SELECT e.*, h.name AS hall_name, c.name AS curator_name
FROM exhibitions e JOIN halls h ON h.id = e.hall_id
JOIN curators c ON c.id = e.curator_id WHERE e.id = ?;

-- name: hall_totals
-- 07. Агрегаты: количество, общая, средняя, минимальная, максимальная вместимость.
SELECT COUNT(*) AS count, COALESCE(SUM(capacity), 0) AS total,
       COALESCE(AVG(capacity), 0) AS average,
       COALESCE(MIN(capacity), 0) AS minimum,
       COALESCE(MAX(capacity), 0) AS maximum FROM halls;

-- name: exhibition_totals
-- 08. Агрегаты: все выставки, неотмененные и отмененные.
SELECT COUNT(*) AS count,
       COALESCE(SUM(CASE WHEN is_cancelled = 0 THEN 1 ELSE 0 END), 0) AS active,
       COALESCE(SUM(is_cancelled), 0) AS cancelled FROM exhibitions;

-- name: exhibitions_by_hall
-- 09. GROUP BY: число неотмененных выставок по залам, включая нулевые значения.
SELECT h.id, h.name, COUNT(e.id) AS count
FROM halls h LEFT JOIN exhibitions e
ON e.hall_id = h.id AND e.is_cancelled = 0
GROUP BY h.id, h.name ORDER BY count DESC, h.id;

-- name: exhibitions_by_curator
-- 10. GROUP BY и HAVING: кураторы с заданным минимумом выставок.
SELECT c.id, c.name, COUNT(e.id) AS count
FROM curators c LEFT JOIN exhibitions e
ON e.curator_id = c.id AND e.is_cancelled = 0
GROUP BY c.id, c.name HAVING COUNT(e.id) >= ? ORDER BY count DESC, c.id;

-- name: exhibition_search
-- 11. Поиск без учета регистра, включая кириллицу; CASEFOLD зарегистрирован в Python.
SELECT e.*, h.name AS hall_name, c.name AS curator_name
FROM exhibitions e JOIN halls h ON h.id = e.hall_id
JOIN curators c ON c.id = e.curator_id
WHERE CASEFOLD(e.title) LIKE ? ESCAPE '!'
ORDER BY e.start_date, e.id LIMIT ? OFFSET ?;

-- name: hall_detail
-- 12. Карточка зала.
SELECT * FROM halls WHERE id = ?;

-- name: missing_descriptions
-- 13. NULL и пустые описания; показатель полноты каталога в статистике.
SELECT COUNT(*) AS count FROM exhibitions
WHERE description IS NULL OR trim(description) = '';
