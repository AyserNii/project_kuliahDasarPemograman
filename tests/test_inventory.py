import unittest
from modules.inventory import (
    calculate_eoq,
    calculate_safety_stock,
    calculate_reorder_point,
    calculate_inventory_costs,
    analyze_inventory_item,
)


class TestInventoryCalculations(unittest.TestCase):
    def test_calculate_eoq(self):
        # D = 2400, S = 50000, H = 12000
        # EOQ = sqrt((2 * 2400 * 50000) / 12000) = sqrt(20000) ≈ 141.42
        eoq = calculate_eoq(2400, 50000, 12000)
        self.assertAlmostEqual(eoq, 141.42, places=2)

    def test_calculate_safety_stock(self):
        # stddev = 2, L = 5, Z = 1.650
        # SS = 1.650 * 2 * sqrt(5) ≈ 7.38
        ss = calculate_safety_stock(2, 5, 1.650)
        self.assertAlmostEqual(ss, 7.38, places=2)

    def test_calculate_reorder_point(self):
        # avg_d = 8, L = 5, SS = 7.38
        # ROP = (8 * 5) + 7.38 = 47.38
        rop = calculate_reorder_point(8, 5, 7.38)
        self.assertAlmostEqual(rop, 47.38, places=2)

    def test_invalid_parameters_raise_error(self):
        with self.assertRaises(ValueError):
            calculate_eoq(-100, 5000, 200)

        with self.assertRaises(ValueError):
            calculate_safety_stock(-2, 5)

        with self.assertRaises(ValueError):
            calculate_reorder_point(-5, 5, 10)

    def test_inventory_costs(self):
        costs = calculate_inventory_costs(
            annual_demand=2400,
            order_quantity=141.42,
            ordering_cost=50000,
            holding_cost_per_unit_year=12000,
        )
        self.assertGreater(costs["total_cost"], 0)
        self.assertAlmostEqual(costs["annual_ordering_cost"], costs["annual_holding_cost"], delta=100)


if __name__ == "__main__":
    unittest.main()
