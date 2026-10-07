import unittest
import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from delivery_service import calculate_delivery_cost

SEND_DATE = datetime.date(2026, 9, 3)


def parse(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


# =====================================================================
# 1. Валидация входных данных
# =====================================================================
class TestInputValidation(unittest.TestCase):

    def test_weight_below_minimum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(0.05, 100, "обычный"),
                         (-1, "0000-00-00"))

    def test_weight_above_maximum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(50.1, 100, "обычный"),
                         (-1, "0000-00-00"))

    def test_weight_at_minimum_boundary_is_accepted(self):
        cost, _ = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertNotEqual(cost, -1)

    def test_weight_at_maximum_boundary_is_accepted(self):
        cost, _ = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertNotEqual(cost, -1)

    def test_distance_below_minimum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1, 0, "обычный"),
                         (-1, "0000-00-00"))

    def test_distance_above_maximum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1, 5001, "обычный"),
                         (-1, "0000-00-00"))

    def test_distance_at_boundaries_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(1, 1, "обычный")[0], -1)
        self.assertNotEqual(calculate_delivery_cost(1, 5000, "обычный")[0], -1)

    def test_invalid_package_type_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "стекло"),
                         (-1, "0000-00-00"))

    def test_empty_package_type_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1, 100, ""),
                         (-1, "0000-00-00"))


# =====================================================================
# 2. Базовый тариф и весовые коэффициенты
# =====================================================================
class TestTariffAndWeight(unittest.TestCase):

    def test_base_cost_for_light_package(self):
        cost, _ = calculate_delivery_cost(1, 100, "обычный")
        self.assertEqual(cost, 200 + 100 * 5)

    def test_distance_cost_is_linear(self):
        c1, _ = calculate_delivery_cost(1, 100, "обычный")
        c2, _ = calculate_delivery_cost(1, 200, "обычный")
        self.assertEqual(c2 - c1, 500)

    def test_weight_at_5kg_no_coefficient(self):
        cost, _ = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_weight_just_above_5kg_applies_1_2(self):
        cost, _ = calculate_delivery_cost(5.01, 100, "обычный")
        self.assertEqual(cost, int(700 * 1.2))

    def test_weight_in_middle_range_applies_1_2(self):
        cost, _ = calculate_delivery_cost(10, 100, "обычный")
        self.assertEqual(cost, int(700 * 1.2))

    def test_weight_at_20kg_applies_1_5(self):
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, int(700 * 1.5))

    def test_weight_above_20kg_applies_1_5(self):
        cost, _ = calculate_delivery_cost(35, 100, "обычный")
        self.assertEqual(cost, int(700 * 1.5))


# =====================================================================
# 3. Надбавки за тип посылки
# =====================================================================
class TestPackageTypeSurcharge(unittest.TestCase):

    def test_regular_has_no_surcharge(self):
        cost, _ = calculate_delivery_cost(1, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_fragile_adds_300(self):
        cost, _ = calculate_delivery_cost(1, 100, "хрупкий")
        self.assertEqual(cost, 700 + 300)

    def test_dangerous_adds_1000(self):
        cost, _ = calculate_delivery_cost(1, 100, "опасный")
        self.assertEqual(cost, 700 + 1000)


# =====================================================================
# 4. Экспресс-доставка  (здесь ловим баги)
# =====================================================================
class TestExpressDelivery(unittest.TestCase):

    def test_express_costs_more_than_regular(self):
        regular, _ = calculate_delivery_cost(1, 100, "обычный", is_express=False)
        express, _ = calculate_delivery_cost(1, 100, "обычный", is_express=True)
        self.assertGreater(express, regular)

    def test_express_cost_is_double_of_regular(self):
        regular, _ = calculate_delivery_cost(1, 100, "обычный", is_express=False)
        express, _ = calculate_delivery_cost(1, 100, "обычный", is_express=True)
        self.assertEqual(express, regular * 2)

    def test_express_delivery_date_is_after_sending_date(self):
        _, date_str = calculate_delivery_cost(1, 100, "обычный", is_express=True)
        self.assertGreater(parse(date_str), SEND_DATE)

    def test_express_short_distance_takes_one_day(self):
        _, date_str = calculate_delivery_cost(1, 100, "обычный", is_express=True)
        self.assertEqual(parse(date_str), SEND_DATE + datetime.timedelta(days=1))

    def test_express_speedups_long_distance(self):
        _, reg = calculate_delivery_cost(1, 2000, "обычный", is_express=False)
        _, exp = calculate_delivery_cost(1, 2000, "обычный", is_express=True)
        self.assertLess(parse(exp), parse(reg))


# =====================================================================
# 5. Расчёт даты доставки
# =====================================================================
class TestDeliveryDate(unittest.TestCase):

    def test_delivery_starts_from_fixed_date(self):
        _, date_str = calculate_delivery_cost(1, 100, "обычный")
        self.assertEqual(parse(date_str), SEND_DATE + datetime.timedelta(days=1))

    def test_days_scale_with_distance(self):
        _, date_str = calculate_delivery_cost(1, 5000, "обычный")
        self.assertEqual(parse(date_str), SEND_DATE + datetime.timedelta(days=10))

    def test_minimum_one_day_for_short_distance(self):
        _, date_str = calculate_delivery_cost(1, 1, "обычный")
        self.assertEqual(parse(date_str), SEND_DATE + datetime.timedelta(days=1))

    def test_date_format_is_iso(self):
        _, date_str = calculate_delivery_cost(1, 100, "обычный")
        self.assertRegex(date_str, r"^\d{4}-\d{2}-\d{2}$")


# =====================================================================
# 6. Округление стоимости
# =====================================================================
class TestRounding(unittest.TestCase):

    def test_cost_is_rounded_not_truncated(self):
        # weight >= 20 -> ×1.5; distance=101 -> 705; 705 * 1.5 = 1057.5
        cost, _ = calculate_delivery_cost(25, 101, "обычный")
        self.assertEqual(cost, round(705 * 1.5))  # ожидаем 1058


# =====================================================================
# 7. Интеграция и типы возврата
# =====================================================================
class TestIntegration(unittest.TestCase):

    def test_combined_heavy_fragile_express(self):
        cost, date_str = calculate_delivery_cost(25, 1000, "хрупкий", is_express=True)
        self.assertEqual(cost, 16200)
        self.assertEqual(parse(date_str), SEND_DATE + datetime.timedelta(days=1))

    def test_return_type_is_tuple_of_two(self):
        result = calculate_delivery_cost(1, 100, "обычный")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], str)


if __name__ == "__main__":
    unittest.main()