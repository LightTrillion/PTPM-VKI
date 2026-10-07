import unittest
import sys
import os

# Добавляем src/ в sys.path, чтобы Python нашёл my_project во время тестов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from my_project import (
    parse_side, is_triangle, classify_triangle, compute_vertices, process_request
)
# =====================================================================
# 1. Тесты разбора входной строки
# =====================================================================
class TestParseSide(unittest.TestCase):

    def test_parse_positive_integer_returns_ok(self):
        self.assertEqual(parse_side("5"), ("ok", 5.0))

    def test_parse_positive_float_returns_ok(self):
        self.assertEqual(parse_side("3.14"), ("ok", 3.14))

    def test_parse_whitespace_around_number_is_trimmed(self):
        self.assertEqual(parse_side("  7.5  "), ("ok", 7.5))

    def test_parse_empty_string_returns_non_numeric(self):
        self.assertEqual(parse_side(""), ("non_numeric", None))

    def test_parse_letters_returns_non_numeric(self):
        self.assertEqual(parse_side("abc"), ("non_numeric", None))

    def test_parse_none_returns_non_numeric(self):
        self.assertEqual(parse_side(None), ("non_numeric", None))

    def test_parse_zero_returns_invalid(self):
        self.assertEqual(parse_side("0"), ("invalid", None))

    def test_parse_negative_number_returns_invalid(self):
        self.assertEqual(parse_side("-3.5"), ("invalid", None))

    def test_parse_infinity_returns_invalid(self):
        self.assertEqual(parse_side("inf"), ("invalid", None))

    def test_parse_nan_returns_invalid(self):
        self.assertEqual(parse_side("nan"), ("invalid", None))


# =====================================================================
# 2. Тесты проверки неравенства треугольника
# =====================================================================
class TestIsTriangle(unittest.TestCase):

    def test_valid_triangle_returns_true(self):
        self.assertTrue(is_triangle(3, 4, 5))

    def test_degenerate_triangle_returns_false(self):
        self.assertFalse(is_triangle(1, 2, 3))

    def test_sum_less_than_third_side_returns_false(self):
        self.assertFalse(is_triangle(1, 1, 10))

    def test_equilateral_triangle_returns_true(self):
        self.assertTrue(is_triangle(1, 1, 1))

    def test_almost_degenerate_triangle_returns_false(self):
        self.assertFalse(is_triangle(1.0, 1.0, 2.0 + 1e-12))


# =====================================================================
# 3. Тесты классификации вида треугольника
# =====================================================================
class TestClassifyTriangle(unittest.TestCase):

    def test_equilateral_classified_correctly(self):
        self.assertEqual(classify_triangle(1, 1, 1), "равносторонний")

    def test_isosceles_a_equals_b(self):
        self.assertEqual(classify_triangle(5, 5, 3), "равнобедренный")

    def test_isosceles_b_equals_c(self):
        self.assertEqual(classify_triangle(3, 5, 5), "равнобедренный")

    def test_isosceles_a_equals_c(self):
        self.assertEqual(classify_triangle(5, 3, 5), "равнобедренный")

    def test_scalene_classified_correctly(self):
        self.assertEqual(classify_triangle(3, 4, 5), "разносторонний")

    def test_equilateral_is_not_isosceles(self):
        self.assertNotEqual(classify_triangle(2, 2, 2), "равнобедренный")


# =====================================================================
# 4. Тесты расчёта координат вершин
# =====================================================================
class TestComputeVertices(unittest.TestCase):

    def test_returns_three_vertices(self):
        self.assertEqual(len(compute_vertices(3, 4, 5)), 3)

    def test_vertices_are_integer_tuples(self):
        for x, y in compute_vertices(3, 4, 5):
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)

    def test_vertices_fit_inside_field(self):
        for x, y in compute_vertices(3, 4, 5):
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x, 100)
            self.assertLessEqual(y, 100)

    def test_equilateral_vertices_symmetric_by_x(self):
        (x1, _), (x2, _), _ = compute_vertices(1, 1, 1)
        self.assertEqual(x1 + x2, 100)

    def test_third_vertex_higher_than_base(self):
        (_, y1), (_, y2), (_, y3) = compute_vertices(3, 4, 5)
        self.assertLess(y3, y1)

    def test_right_triangle_third_vertex_above_first(self):
        (x1, _), _, (x3, _) = compute_vertices(3, 4, 5)
        self.assertAlmostEqual(x1, x3, delta=1)


# =====================================================================
# 5. Тесты бизнес-логики обработки запроса
# =====================================================================
class TestProcessRequest(unittest.TestCase):

    def test_equilateral_request_returns_correct_type(self):
        tri_type, _ = process_request(["1", "1", "1"])
        self.assertEqual(tri_type, "равносторонний")

    def test_isosceles_request_returns_correct_type(self):
        tri_type, _ = process_request(["5", "5", "3"])
        self.assertEqual(tri_type, "равнобедренный")

    def test_scalene_request_returns_correct_type(self):
        tri_type, _ = process_request(["3", "4", "5"])
        self.assertEqual(tri_type, "разносторонний")

    def test_non_triangle_numeric_returns_minus_one_coords(self):
        tri_type, verts = process_request(["1", "1", "10"])
        self.assertEqual(tri_type, "не треугольник")
        self.assertEqual(verts, [(-1, -1), (-1, -1), (-1, -1)])

    def test_zero_side_returns_minus_one_coords(self):
        tri_type, verts = process_request(["0", "4", "5"])
        self.assertEqual(tri_type, "не треугольник")
        self.assertEqual(verts, [(-1, -1), (-1, -1), (-1, -1)])

    def test_negative_side_returns_minus_one_coords(self):
        _, verts = process_request(["-3", "4", "5"])
        self.assertEqual(verts, [(-1, -1), (-1, -1), (-1, -1)])

    def test_non_numeric_returns_empty_type(self):
        tri_type, _ = process_request(["abc", "4", "5"])
        self.assertEqual(tri_type, "")

    def test_non_numeric_returns_minus_two_coords(self):
        _, verts = process_request(["abc", "4", "5"])
        self.assertEqual(verts, [(-2, -2), (-2, -2), (-2, -2)])

    def test_empty_string_treated_as_non_numeric(self):
        tri_type, verts = process_request(["", "4", "5"])
        self.assertEqual(tri_type, "")
        self.assertEqual(verts, [(-2, -2), (-2, -2), (-2, -2)])

    def test_mixed_invalid_beats_non_numeric(self):
        tri_type, verts = process_request(["abc", "-1", "5"])
        self.assertEqual(tri_type, "")
        self.assertEqual(verts, [(-2, -2), (-2, -2), (-2, -2)])

    def test_float_sides_processed_correctly(self):
        tri_type, _ = process_request(["1.5", "1.5", "1.5"])
        self.assertEqual(tri_type, "равносторонний")

    def test_independence_of_calls(self):
        t1, _ = process_request(["1", "1", "1"])
        t2, _ = process_request(["3", "4", "5"])
        self.assertEqual(t1, "равносторонний")
        self.assertEqual(t2, "разносторонний")


if __name__ == "__main__":
    unittest.main()