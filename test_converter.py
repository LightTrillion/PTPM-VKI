import unittest

from converter import Converter


class TestConverter(unittest.TestCase):

    def test_range_100_7_and_above(self):
        """
        Проверка диапазона [100.7; +inf)
        """
        values = [100.7, 100.8, 101.0, 999.9, 100000.0]

        for x in values:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), 1000)

    def test_positive_below_100_7(self):
        """
        Проверка диапазона (0; 100.7)
        """
        cases = [
            (0.1, 0),
            (0.9, 0),
            (1.0, 1),
            (2.9, 2),
            (65.7, 65),
            (99.9, 99),
            (100.6, 100),
        ]

        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_zero_raises_value_error(self):
        """
        Проверка генерации ValueError при x == 0.0
        """
        for x in (0.0, -0.0):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    Converter.do(x)

    def test_negative_from_minus_30_4_to_zero(self):
        """
        Проверка диапазона [-30.4; 0)
        """
        cases = [
            (-0.1, -5),
            (-0.9, -5),
            (-1.0, -6),
            (-2.5, -7),
            (-10.3, -15),
            (-30.3, -35),
            (-30.4, -35),
        ]

        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_less_or_equal_minus_30_5(self):
        """
        Проверка диапазона (-inf; -30.5]
        """
        values = [-30.5, -30.6, -31.0, -99.9, -1000.0]

        for x in values:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), -2000)

    def test_boundary_values(self):
        """
        Проверка граничных значений между диапазонами
        """

        # Граница между (0; 100.7) и [100.7; +inf)
        self.assertEqual(Converter.do(100.6), 100)
        self.assertEqual(Converter.do(100.7), 1000)

        # Граница около нуля
        self.assertEqual(Converter.do(0.1), 0)
        self.assertEqual(Converter.do(-0.1), -5)

        # Граница между [-30.4; 0) и (-inf; -30.5]
        self.assertEqual(Converter.do(-30.4), -35)
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_return_type_is_int(self):
        """
        Проверка, что метод возвращает именно int
        """
        values = [100.7, 50.5, -10.2, -50.0]

        for x in values:
            with self.subTest(x=x):
                self.assertIsInstance(Converter.do(x), int)


if __name__ == "__main__":
    unittest.main()