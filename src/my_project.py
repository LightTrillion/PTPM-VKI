import logging
import sys
import os
import math

LOG_DIR = "Logs"


def setup_logging():
    """Настройка логгера: файл + консоль."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(LOG_DIR, "file_txt.log"), encoding="utf-8"),
        ],
    )


def parse_side(raw):
    """
    Разбирает входную строку.
    Возвращает (status, value):
      'ok'          — корректное положительное float;
      'non_numeric' — не число / пусто / None;
      'invalid'     — число <= 0, inf, nan.
    """
    if raw is None:
        return "non_numeric", None
    s = str(raw).strip()
    if not s:
        return "non_numeric", None
    try:
        num = float(s)
    except ValueError:
        return "non_numeric", None
    if not math.isfinite(num) or num <= 0:
        return "invalid", None
    return "ok", num


def is_triangle(a, b, c, eps=1e-9):
    """Проверка неравенства треугольника."""
    return (a + b > c + eps) and (a + c > b + eps) and (b + c > a + eps)


def classify_triangle(a, b, c, eps=1e-6):
    """Классификация треугольника по трём сторонам."""
    if abs(a - b) < eps and abs(b - c) < eps:
        return "равносторонний"
    if abs(a - b) < eps or abs(b - c) < eps or abs(a - c) < eps:
        return "равнобедренный"
    return "разносторонний"


def compute_vertices(a, b, c, field=100, padding=10):
    """Координаты трёх вершин треугольника в поле field×field пикселей."""
    x3 = (a * a + b * b - c * c) / (2.0 * a)
    y_sq = b * b - x3 * x3
    if y_sq < 0:
        y_sq = 0.0
    y3 = math.sqrt(y_sq)

    pts = [(0.0, 0.0), (a, 0.0), (x3, y3)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x
    height = max_y - min_y
    avail = field - 2 * padding
    scale = 1.0
    if width > 0 and height > 0:
        scale = min(avail / width, avail / height)
    elif width > 0:
        scale = avail / width
    elif height > 0:
        scale = avail / height

    result = []
    for (x, y) in pts:
        nx = (x - min_x) * scale + padding
        ny = (max_y - y) * scale + padding
        result.append((int(round(nx)), int(round(ny))))
    return result


def process_request(lines):
    """
    Основная логика: принимает список из 3 строк.
    Возвращает (тип_треугольника: str, вершины: list of tuple).
    """
    logging.debug(f"Начало обработки запроса, строки={lines!r}")

    statuses, values = [], []
    for raw in lines:
        st, val = parse_side(raw)
        statuses.append(st)
        values.append(val)

    # 1. Нечисловые данные -> пустая строка, координаты (-2,-2)
    if any(st == "non_numeric" for st in statuses):
        logging.error(f"Невалидные (нечисловые) данные: {lines}")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    # 2. Числовые, но некорректные (<=0, inf, nan) -> не треугольник
    if any(st == "invalid" for st in statuses):
        logging.error(f"Ошибочные числовые данные: {lines}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    a, b, c = values

    # 3. Проверка неравенства треугольника
    if not is_triangle(a, b, c):
        logging.warning(f"Стороны не образуют треугольник: A={a}, B={b}, C={c}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 4. Успешный расчёт
    tri_type = classify_triangle(a, b, c)
    vertices = compute_vertices(a, b, c)
    logging.info(f"Успех: A={a}, B={b}, C={c} -> '{tri_type}', {vertices}")
    return tri_type, vertices


def Main():
    setup_logging()
    logging.info("Приложение запущено")
    try:
        lines = [input() for _ in range(3)]
        tri_type, vertices = process_request(lines)
        print(tri_type)
        print(vertices)
    except Exception:
        logging.exception("Заход в блок обработки исключения:")
        print("")
        print([(-2, -2), (-2, -2), (-2, -2)])
    logging.info("Приложение завершено")


if __name__ == "__main__":
    Main()