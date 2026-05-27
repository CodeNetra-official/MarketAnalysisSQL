"""Market research and price comparison database application.

This project intentionally uses only Python's standard library so that
students can focus on SQL and run it immediately with SQLite.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "market_research.db"
DEFAULT_DATASET = PROJECT_ROOT / "data" / "product_prices.csv"
SQLITE_SCHEMA = PROJECT_ROOT / "sql" / "schema_sqlite.sql"


def connect(database: Path) -> sqlite3.Connection:
    """Open a database connection configured for this project."""
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database: Path, reset: bool = False) -> None:
    """Create an empty database using the SQLite schema."""
    if reset and database.exists():
        database.unlink()
    with connect(database) as connection:
        connection.executescript(SQLITE_SCHEMA.read_text(encoding="utf-8"))


def _lookup_id(
    connection: sqlite3.Connection, table: str, id_column: str, name_column: str, name: str
) -> int:
    connection.execute(
        f"INSERT OR IGNORE INTO {table} ({name_column}) VALUES (?)", (name,)
    )
    result = connection.execute(
        f"SELECT {id_column} FROM {table} WHERE {name_column} = ?", (name,)
    ).fetchone()
    if result is None:
        raise RuntimeError(f"Could not find or insert {name} in {table}.")
    return int(result[id_column])


def import_dataset(database: Path, dataset: Path = DEFAULT_DATASET) -> int:
    """Import CSV observations, updating matching product/retailer/date rows."""
    with dataset.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    with connect(database) as connection:
        for row in rows:
            category_id = _lookup_id(
                connection, "categories", "category_id", "category_name", row["category"]
            )
            brand_id = _lookup_id(
                connection, "brands", "brand_id", "brand_name", row["brand"]
            )
            retailer_id = _lookup_id(
                connection, "retailers", "retailer_id", "retailer_name", row["retailer"]
            )

            connection.execute(
                """
                INSERT INTO products (
                    product_key, product_name, brand_id, category_id, model_number
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(product_key) DO UPDATE SET
                    product_name = excluded.product_name,
                    brand_id = excluded.brand_id,
                    category_id = excluded.category_id,
                    model_number = excluded.model_number
                """,
                (
                    row["product_key"],
                    row["product_name"],
                    brand_id,
                    category_id,
                    row["model_number"],
                ),
            )
            product_id = connection.execute(
                "SELECT product_id FROM products WHERE product_key = ?",
                (row["product_key"],),
            ).fetchone()["product_id"]

            connection.execute(
                """
                INSERT INTO price_observations (
                    product_id, retailer_id, listing_reference, listed_price_inr,
                    original_price_inr, rating, review_count, in_stock, captured_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(product_id, retailer_id, captured_date) DO UPDATE SET
                    listing_reference = excluded.listing_reference,
                    listed_price_inr = excluded.listed_price_inr,
                    original_price_inr = excluded.original_price_inr,
                    rating = excluded.rating,
                    review_count = excluded.review_count,
                    in_stock = excluded.in_stock
                """,
                (
                    product_id,
                    retailer_id,
                    row["listing_reference"],
                    row["listed_price_inr"],
                    row["original_price_inr"],
                    row["rating"],
                    row["review_count"],
                    row["in_stock"],
                    row["captured_date"],
                ),
            )
    return len(rows)


def database_counts(database: Path) -> dict[str, int]:
    with connect(database) as connection:
        return {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("products", "retailers", "price_observations")
        }


def comparison_report(database: Path, category: str | None = None) -> list[sqlite3.Row]:
    """Return the cheapest in-stock offer and saving opportunity per product."""
    category_filter = "AND c.category_name = ?" if category else ""
    parameters: tuple[Any, ...] = (category,) if category else ()
    query = f"""
        WITH ranked AS (
            SELECT
                p.product_name,
                c.category_name,
                r.retailer_name,
                po.listed_price_inr,
                ROW_NUMBER() OVER (
                    PARTITION BY p.product_id ORDER BY po.listed_price_inr, r.retailer_name
                ) AS price_rank,
                MAX(po.listed_price_inr) OVER (PARTITION BY p.product_id) AS highest_price
            FROM price_observations po
            JOIN products p ON p.product_id = po.product_id
            JOIN categories c ON c.category_id = p.category_id
            JOIN retailers r ON r.retailer_id = po.retailer_id
            WHERE po.in_stock = 1 {category_filter}
        )
        SELECT
            product_name,
            category_name,
            retailer_name AS cheapest_retailer,
            listed_price_inr AS lowest_price,
            highest_price,
            highest_price - listed_price_inr AS possible_saving
        FROM ranked
        WHERE price_rank = 1
        ORDER BY possible_saving DESC, product_name
    """
    with connect(database) as connection:
        return list(connection.execute(query, parameters))


def run_crud_demo(database: Path) -> dict[str, sqlite3.Row | int]:
    """Execute CRUD operations on one temporary listing and return the evidence."""
    with connect(database) as connection:
        product = connection.execute(
            "SELECT product_id FROM products WHERE product_key = 'LOG-M331'"
        ).fetchone()
        if product is None:
            raise RuntimeError("Run setup first so the Logitech demo product exists.")
        retailer_id = _lookup_id(
            connection, "retailers", "retailer_id", "retailer_name", "Demo Electronics"
        )
        connection.execute(
            "DELETE FROM price_observations WHERE listing_reference = 'DEMO-M331'"
        )

        connection.execute(
            """
            INSERT INTO price_observations (
                product_id, retailer_id, listing_reference, listed_price_inr,
                original_price_inr, rating, review_count, in_stock, captured_date
            ) VALUES (?, ?, 'DEMO-M331', 859.00, 1295.00, 4.3, 25, 1, '2026-05-21')
            """,
            (product["product_id"], retailer_id),
        )
        created = connection.execute(
            "SELECT listing_reference, listed_price_inr FROM price_observations "
            "WHERE listing_reference = 'DEMO-M331'"
        ).fetchone()

        read_row = connection.execute(
            """
            SELECT p.product_name, r.retailer_name, po.listed_price_inr
            FROM price_observations po
            JOIN products p ON p.product_id = po.product_id
            JOIN retailers r ON r.retailer_id = po.retailer_id
            WHERE po.listing_reference = 'DEMO-M331'
            """
        ).fetchone()

        connection.execute(
            "UPDATE price_observations SET listed_price_inr = 829.00 "
            "WHERE listing_reference = 'DEMO-M331'"
        )
        updated = connection.execute(
            "SELECT listing_reference, listed_price_inr FROM price_observations "
            "WHERE listing_reference = 'DEMO-M331'"
        ).fetchone()

        deleted = connection.execute(
            "DELETE FROM price_observations WHERE listing_reference = 'DEMO-M331'"
        ).rowcount

    return {"created": created, "read": read_row, "updated": updated, "deleted": deleted}


def rupees(value: float) -> str:
    return f"INR {float(value):,.2f}"


def print_report(rows: list[sqlite3.Row]) -> None:
    print("PRICE COMPARISON REPORT (only in-stock listings)")
    print("-" * 105)
    print(f"{'Product':37} {'Category':20} {'Cheapest at':18} {'Price':>12} {'Save':>12}")
    print("-" * 105)
    for row in rows:
        print(
            f"{row['product_name'][:37]:37} {row['category_name'][:20]:20} "
            f"{row['cheapest_retailer'][:18]:18} {rupees(row['lowest_price']):>12} "
            f"{rupees(row['possible_saving']):>12}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Market research price comparison database")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = subparsers.add_parser("setup", help="Create schema and import the CSV dataset")
    setup.add_argument("--reset", action="store_true", help="Delete and recreate the database")
    setup.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)

    load = subparsers.add_parser("import-data", help="Import or refresh CSV price observations")
    load.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)

    subparsers.add_parser("stats", help="Show table row counts")
    report = subparsers.add_parser("report", help="Show cheapest prices and savings")
    report.add_argument("--category", help="Only display one category")
    subparsers.add_parser("crud-demo", help="Run and display CREATE, READ, UPDATE, DELETE")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "setup":
        initialize_database(args.database, args.reset)
        count = import_dataset(args.database, args.dataset)
        print(f"Database ready: {args.database}")
        print(f"Imported {count} price observations.")
    elif args.command == "import-data":
        initialize_database(args.database)
        count = import_dataset(args.database, args.dataset)
        print(f"Imported or refreshed {count} price observations.")
    elif args.command == "stats":
        for table, count in database_counts(args.database).items():
            print(f"{table}: {count}")
    elif args.command == "report":
        print_report(comparison_report(args.database, args.category))
    elif args.command == "crud-demo":
        result = run_crud_demo(args.database)
        print("CREATE:", dict(result["created"]))
        print("READ:  ", dict(result["read"]))
        print("UPDATE:", dict(result["updated"]))
        print("DELETE:", f"{result['deleted']} row removed")


if __name__ == "__main__":
    main()
