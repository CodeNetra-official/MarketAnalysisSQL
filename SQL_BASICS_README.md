# SQL Basics: Market Research and Price Comparison

## Class Goal

In this 90-minute class, students will build and query a small market research
database. By the end, they should be able to explain tables and keys, run
basic `SELECT` queries, perform CRUD operations, and compare a product's price
across retailers.

The classroom uses **SQLite** because it runs from one database file and does
not require setting up a database server. MySQL equivalents are provided in
the `sql/` folder for later practice.

## What Fits In 1.5 Hours?

The following version fits comfortably for beginners:

| Time | Topic | Student Outcome |
| --- | --- | --- |
| 0-10 min | Project story and dataset | Understand the problem: compare product prices |
| 10-22 min | Database and SQL basics | Know table, row, column, primary key, foreign key |
| 22-32 min | Setup SQLite database | Import 30 observations and view table counts |
| 32-45 min | `SELECT`, `WHERE`, `ORDER BY` | Filter and sort product/price data |
| 45-62 min | CRUD operations | Insert, read, update, and delete one demo listing |
| 62-77 min | `JOIN` price comparison | Combine products, retailers, and prices |
| 77-87 min | Student challenge | Answer questions with queries |
| 87-90 min | Recap / exit question | State what CRUD and a `JOIN` do |

Do not try to install/configure MySQL live during this session. Show the MySQL
scripts briefly at the end or give them as homework.

## Files Students Use

| File | Why It Matters |
| --- | --- |
| `data/product_prices.csv` | Source dataset with product listings |
| `sql/schema_sqlite.sql` | Tables, keys, validation rules, and indexes |
| `sql/crud_queries_sqlite.sql` | Full CRUD demonstration |
| `src/market_research_db.py` | Creates/imports the database automatically |
| `data/market_research.db` | SQLite database created during the class |

## SQL Vocabulary

| Term | Meaning | Project Example |
| --- | --- | --- |
| Database | Organized collection of data | `market_research.db` |
| Table | Data stored by subject | `products`, `retailers` |
| Row | One record | One retailer price observation |
| Column | One attribute | `listed_price_inr` |
| Primary key | Unique ID for one row | `product_id` |
| Foreign key | Link to a row in another table | `product_id` inside `price_observations` |
| Query | SQL instruction sent to the database | `SELECT * FROM products;` |
| Constraint | Rule protecting data quality | Price must be greater than zero |

## Why More Than One Table?

If a product is offered by three retailers, its name and brand should not need
to be typed three times inside a products table. This project separates:

| Table | Stores |
| --- | --- |
| `categories` | Category names, such as Audio |
| `brands` | Brand names, such as Sony |
| `products` | One row per product |
| `retailers` | One row per store |
| `price_observations` | A product price at one retailer on one date |

This design reduces repeated information and enables accurate comparison.

## Step 1: Create The Database

Open a terminal in this project folder:

```bash
cd "/Users/saichandrareddy/Documents/New project/market-research-price-comparison"
python3 src/market_research_db.py setup --reset
python3 src/market_research_db.py stats
```

Expected counts:

```text
products: 10
retailers: 4
price_observations: 30
```

Now enter the SQLite shell:

```bash
sqlite3 data/market_research.db
```

Improve query output inside SQLite:

```sql
.headers on
.mode column
.tables
```

To leave SQLite later, use:

```sql
.quit
```

## Step 2: Read Data With `SELECT`

`SELECT` chooses columns to display. `FROM` chooses the table.

```sql
SELECT product_id, product_name, model_number
FROM products;
```

Use `LIMIT` when exploring a larger table:

```sql
SELECT *
FROM price_observations
LIMIT 5;
```

## Step 3: Filter And Sort Data

`WHERE` filters rows. `ORDER BY` sorts the result.

```sql
SELECT listing_reference, listed_price_inr, rating
FROM price_observations
WHERE listed_price_inr < 1000
ORDER BY listed_price_inr ASC;
```

Count observations:

```sql
SELECT COUNT(*) AS number_of_prices
FROM price_observations;
```

Calculate an average:

```sql
SELECT ROUND(AVG(listed_price_inr), 2) AS average_listed_price
FROM price_observations;
```

## Step 4: Understand CRUD

CRUD represents the four operations used in most database applications:

| CRUD | SQL | Purpose |
| --- | --- | --- |
| Create | `INSERT` | Add data |
| Read | `SELECT` | View data |
| Update | `UPDATE` | Change data |
| Delete | `DELETE` | Remove data |

### Create

Add a sample retailer first:

```sql
INSERT OR IGNORE INTO retailers (retailer_name)
VALUES ('Classroom Store');
```

Add a price for the Logitech mouse:

```sql
INSERT INTO price_observations (
    product_id, retailer_id, listing_reference, listed_price_inr,
    original_price_inr, rating, review_count, in_stock, captured_date
)
SELECT p.product_id, r.retailer_id, 'CLASS-M331', 850.00,
       1295.00, 4.1, 10, 1, '2026-05-26'
FROM products p
JOIN retailers r ON r.retailer_name = 'Classroom Store'
WHERE p.product_key = 'LOG-M331';
```

### Read

```sql
SELECT listing_reference, listed_price_inr, captured_date
FROM price_observations
WHERE listing_reference = 'CLASS-M331';
```

### Update

Always use `WHERE` when changing a specific row.

```sql
UPDATE price_observations
SET listed_price_inr = 825.00
WHERE listing_reference = 'CLASS-M331';
```

Confirm the change:

```sql
SELECT listing_reference, listed_price_inr
FROM price_observations
WHERE listing_reference = 'CLASS-M331';
```

### Delete

Always preview the target with `SELECT` before deleting it.

```sql
DELETE FROM price_observations
WHERE listing_reference = 'CLASS-M331';
```

Confirm that no classroom listing remains:

```sql
SELECT *
FROM price_observations
WHERE listing_reference = 'CLASS-M331';
```

## Step 5: Combine Tables With `JOIN`

The price table stores IDs, not product or retailer names. A `JOIN` connects
related tables so the result is meaningful to a reader.

```sql
SELECT
    p.product_name,
    r.retailer_name,
    po.listed_price_inr
FROM price_observations po
JOIN products p ON p.product_id = po.product_id
JOIN retailers r ON r.retailer_id = po.retailer_id
WHERE p.product_key = 'SONY-WHCH520'
ORDER BY po.listed_price_inr ASC;
```

Ask students: which retailer offers the cheapest Sony headphones?

## Step 6: Run The Prepared Comparison

The provided script demonstrates CRUD and then displays each product's
cheapest in-stock price.

From inside SQLite:

```sql
.read sql/crud_queries_sqlite.sql
```

Or from the normal terminal:

```bash
python3 src/market_research_db.py report
```

The largest saving in the sample dataset is for the HP laptop:

```text
Lowest price: INR 50,990.00
Highest price: INR 53,490.00
Possible saving: INR 2,500.00
```

## SQLite And MySQL: Quick Difference

| Topic | SQLite Used In Class | MySQL Reference |
| --- | --- | --- |
| Setup | One local `.db` file | Database server must run |
| Auto ID | `AUTOINCREMENT` | `AUTO_INCREMENT` |
| Ignore duplicate | `INSERT OR IGNORE` | `INSERT IGNORE` |
| Boolean value | `0` or `1` | `FALSE` or `TRUE` |

The idea of CRUD and joins is the same in both systems; some setup and syntax
details differ.

## Student Challenge Queries

Give students 10 minutes and ask them to write queries for these tasks:

1. Show all products in the `Audio` category by joining `products` and
   `categories`.
2. List in-stock observations from cheapest to most expensive.
3. Find the number of product observations available from each retailer.
4. Display the cheapest price of `JBL Flip 6 Portable Bluetooth Speaker`.

Possible answers:

```sql
SELECT p.product_name
FROM products p
JOIN categories c ON c.category_id = p.category_id
WHERE c.category_name = 'Audio';

SELECT listing_reference, listed_price_inr
FROM price_observations
WHERE in_stock = 1
ORDER BY listed_price_inr;

SELECT r.retailer_name, COUNT(*) AS observations
FROM price_observations po
JOIN retailers r ON r.retailer_id = po.retailer_id
GROUP BY r.retailer_name
ORDER BY observations DESC;

SELECT MIN(po.listed_price_inr) AS lowest_price
FROM price_observations po
JOIN products p ON p.product_id = po.product_id
WHERE p.product_name = 'JBL Flip 6 Portable Bluetooth Speaker'
  AND po.in_stock = 1;
```

## Exit Questions

1. What do the letters in CRUD represent?
2. Why does `price_observations` store `product_id` instead of repeating all
   product details?
3. Why is `WHERE` especially important with `UPDATE` and `DELETE`?
4. When do we use a `JOIN`?

## Optional Homework

1. Run `python3 src/market_research_db.py report --category Audio`.
2. Write a query to find each category's lowest available price.
3. Read `sql/schema_mysql.sql` and identify two syntax differences from
   SQLite.
