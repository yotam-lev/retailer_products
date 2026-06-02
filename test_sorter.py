import unittest
from src.sorter import Sorter

class TestSorter(unittest.TestCase):
    def test_sort_products_success(self):
        products = [
            {"id": 1, "price": 20},
            {"id": 2, "price": 10},
            {"id": 3, "price": 30}
        ]
        sorted_products = Sorter.sort_products(products, "price")
        self.assertEqual(sorted_products[0]["price"], 10)
        self.assertEqual(sorted_products[2]["price"], 30)

    def test_sort_products_missing_key(self):
        products = [
            {"id": 1, "price": 20},
            {"id": 2}, # missing price
            {"id": 3, "price": 30}
        ]
        # Should not raise exception, missing key treated as empty string ""
        sorted_products = Sorter.sort_products(products, "price")
        print(f"these are the sorted products{sorted_products}")
        self.assertEqual(len(sorted_products), 3)
        

    def test_sort_products_reverse(self):
        products = [
            {"id": 1, "price": 20},
            {"id": 2, "price": 10}
        ]
        sorted_products = Sorter.sort_products(products, "price", reverse=True)
        print(f"these are sorted")
        self.assertEqual(sorted_products[0]["price"], 20)

if __name__ == '__main__':
    unittest.main()
