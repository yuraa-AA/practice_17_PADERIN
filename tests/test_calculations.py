import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculations import (
    calc_contact_pressure,
    calc_volume_and_areas,
    divided_differences,
    expansion,
    expansion_alpha_table,
    expansion_temperature_table,
    integral_results,
    lagrange_value,
    mean_friction,
    newton_value,
    variant17_nodes,
)
from frame_balance import balance_by_transverse_axis
from input_validator import parse_float_list, require_odd, to_float


class TestTask1(unittest.TestCase):
    def test_volume_and_areas_control_values(self):
        result = calc_volume_and_areas(2, 5)
        self.assertEqual(result.volume, 20)
        self.assertEqual(result.side_area, 40)
        self.assertEqual(result.full_area, 48)

    def test_volume_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            calc_volume_and_areas(-2, 5)


class TestTask2(unittest.TestCase):
    def test_mean_friction_for_steel_aluminum(self):
        self.assertAlmostEqual(mean_friction("сталь-алюминий"), 0.04)

    def test_contact_pressure_formula(self):
        expected = (2 * 100 * 1.5) / (0.04 * math.pi * 20**2 * 50)
        self.assertAlmostEqual(calc_contact_pressure(100, 1.5, 0.04, 20, 50), expected)


class TestTask3And4(unittest.TestCase):
    def test_expansion_control_value(self):
        self.assertAlmostEqual(expansion(250, 12e-6, 60), 0.18)

    def test_temperature_table_is_independent_and_has_expected_last_value(self):
        table = expansion_temperature_table()
        self.assertEqual(table[0], (20, 0.0))
        self.assertAlmostEqual(table[-1][1], 0.18)

    def test_alpha_table_count(self):
        table = expansion_alpha_table()
        self.assertEqual(len(table), 25)


class TestTask5(unittest.TestCase):
    def test_balance_matrix_size_and_percent(self):
        result = balance_by_transverse_axis(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(len(result.matrix), 3)
        self.assertEqual(len(result.matrix[0]), 3)
        self.assertLessEqual(result.difference_percent, 15)

    def test_balance_rejects_even_n(self):
        with self.assertRaises(ValueError):
            balance_by_transverse_axis(2, [1, 2, 3, 4])


class TestTask6(unittest.TestCase):
    def test_lagrange_matches_nodes(self):
        x_nodes, y_nodes = variant17_nodes()
        for x, y in zip(x_nodes, y_nodes):
            self.assertAlmostEqual(lagrange_value(x_nodes, y_nodes, x), y)

    def test_newton_and_lagrange_are_close(self):
        x_nodes, y_nodes = variant17_nodes()
        coef = divided_differences(x_nodes, y_nodes)
        point = x_nodes[1] + 10.8 / 8
        self.assertAlmostEqual(lagrange_value(x_nodes, y_nodes, point), newton_value(x_nodes, coef, point), places=7)


class TestTask7(unittest.TestCase):
    def test_integral_methods_return_positive_values(self):
        rect, trap, simp = integral_results()
        self.assertGreater(rect, 0)
        self.assertGreater(trap, 0)
        self.assertGreater(simp, 0)


class TestValidators(unittest.TestCase):
    def test_to_float_accepts_comma(self):
        self.assertEqual(to_float("1,5"), 1.5)

    def test_parse_float_list_expected_count(self):
        self.assertEqual(parse_float_list("1, 2, 3", 3), [1.0, 2.0, 3.0])

    def test_require_odd_rejects_even(self):
        with self.assertRaises(ValueError):
            require_odd(4)


if __name__ == "__main__":
    unittest.main()
