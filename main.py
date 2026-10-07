import logging
import sys
import os
import math

# --- Создание папки для логов (до настройки хендлера) ---
LOG_DIR = "Logs"
os.makedirs(LOG_DIR, exist_ok=True)

# --- Конфигурация логгера: одновременно в консоль и в файл ---
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

# ---------------------------------------------------------------------------
#  Вспомогательные функции
# ---------------------------------------------------------------------------

def parse_side(raw: str):
    """
    Разбирает входную строку.
    Возвращает кортеж (status, value), где status:
      'ok'          — корректное положительное float-число;
      'non_numeric' — строка не является числом (или пустая);
      'invalid'     — число, но не положительное / не конечное.
    """
    if raw is None:
        return "non_numeric", None

    s = raw.strip()
    if not s:
        return "non_numeric", None

    try:
        num = float(s)
    except ValueError:
        return "non_numeric", None

    if not math.isfinite(num) or num <= 0:
        return "invalid", None

    return "ok", num


def is_triangle(a: float, b: float, c: float, eps: float = 1e-9) -> bool:
    """Проверка неравенства треугольника (строгое)."""
    return (a + b > c + eps) and (a + c > b + eps) and (b + c > a + eps)


def classify_triangle(a: float, b: float, c: float, eps: float = 1e-6) -> str:
    """Определяет вид треугольника по трём сторонам."""
    if abs(a - b) < eps and abs(b - c) < eps:
        return "равносторонний"
    if abs(a - b) < eps or abs(b - c) < eps or abs(a - c) < eps:
        return "равнобедренный"
    return "разносторонний"


def compute_vertices(a: float, b: float, c: float,
                     field: int = 100, padding: int = 10):
    """
    Вычисляет координаты вершин треугольника, укладывая его в поле field x field px.
    Сторона A кладётся горизонтально внизу.
    Возвращает список из 3 кортежей (int, int).
    """
    # Кладём первую вершину в (0,0), вторую — в (a, 0).
    # Третья вершина: расстояние b от (0,0) и c от (a,0).
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

    # Переносим в положительную область и инвертируем Y (координаты экрана).
    result = []
    for (x, y) in pts:
        nx = (x - min_x) * scale + padding
        ny = (max_y - y) * scale + padding
        result.append((int(round(nx)), int(round(ny))))

    return result


# ---------------------------------------------------------------------------
#  Бизнес-логика запроса
# ---------------------------------------------------------------------------

def process_request(lines):
    """
    lines: список из трёх строк (входные данные).
    Возвращает (triangle_type, vertices).
    """
    logging.debug(f"Начало обработки запроса, строки={lines!r}")

    statuses = []
    values = []
    for raw in lines:
        st, val = parse_side(raw)
        statuses.append(st)
        values.append(val)

    # 1. Нечисловые данные -> пустая строка, координаты (-2, -2)
    if any(st == "non_numeric" for st in statuses):
        logging.error(f"Невалидные (нечисловые) данные: {lines}")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    # 2. Числовые, но некорректные (<=0, inf, nan) -> не треугольник, (-1,-1)
    if any(st == "invalid" for st in statuses):
        logging.error(f"Ошибочные числовые данные (не положительные/не конечные): {lines}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    a, b, c = values

    # 3. Проверка неравенства треугольника
    if not is_triangle(a, b, c):
        logging.warning(f"Стороны не образуют треугольник: A={a}, B={b}, C={c}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 4. Успешный расчёт
    tri_type = classify_triangle(a, b, c)
    vertices = compute_vertices(a, b, c)
    logging.info(
        f"Успешный запрос: A={a}, B={b}, C={c} -> тип='{tri_type}', вершины={vertices}"
    )
    return tri_type, vertices


# ---------------------------------------------------------------------------
#  Точка входа
# ---------------------------------------------------------------------------

def Main():
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    try:
        lines = []
        for _ in range(3):
            lines.append(input())

        tri_type, vertices = process_request(lines)

        # Вывод результата
        print(tri_type)
        print(vertices)

    except Exception:
        # Автоматически подцепляет traceback
        logging.error("Что-то пошло не так...")
        logging.exception("Заход в блок обработки исключения:")
        # При сбое выводим безопасный результат, не завершая аварийно
        print("")
        print([(-2, -2), (-2, -2), (-2, -2)])

    logging.info("Приложение завершено")


if __name__ == "__main__":
    Main()