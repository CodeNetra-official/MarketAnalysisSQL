import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from market_research_db import (  # noqa: E402
    comparison_report,
    database_counts,
    import_dataset,
    initialize_database,
    run_crud_demo,
)


class MarketResearchDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.database)
        import_dataset(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_dataset_imports_normalized_records(self) -> None:
        self.assertEqual(
            database_counts(self.database),
            {"products": 10, "retailers": 4, "price_observations": 30},
        )

    def test_reimport_is_idempotent(self) -> None:
        import_dataset(self.database)
        self.assertEqual(database_counts(self.database)["price_observations"], 30)

    def test_report_orders_products_by_available_saving(self) -> None:
        report = comparison_report(self.database)
        self.assertEqual(report[0]["product_name"], "HP 15s 12th Gen i5 Laptop")
        self.assertEqual(float(report[0]["possible_saving"]), 2500.00)

    def test_crud_demo_deletes_demo_observation_when_finished(self) -> None:
        result = run_crud_demo(self.database)
        self.assertEqual(float(result["created"]["listed_price_inr"]), 859.00)
        self.assertEqual(float(result["updated"]["listed_price_inr"]), 829.00)
        self.assertEqual(result["deleted"], 1)
        self.assertEqual(database_counts(self.database)["price_observations"], 30)


if __name__ == "__main__":
    unittest.main()
