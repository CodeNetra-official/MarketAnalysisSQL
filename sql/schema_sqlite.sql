PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS brands (
    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS retailers (
    retailer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    retailer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_key TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    brand_id INTEGER NOT NULL REFERENCES brands(brand_id),
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    model_number TEXT NOT NULL,
    UNIQUE (brand_id, model_number)
);

CREATE TABLE IF NOT EXISTS price_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    retailer_id INTEGER NOT NULL REFERENCES retailers(retailer_id),
    listing_reference TEXT NOT NULL,
    listed_price_inr NUMERIC NOT NULL CHECK (listed_price_inr > 0),
    original_price_inr NUMERIC NOT NULL CHECK (original_price_inr >= listed_price_inr),
    rating NUMERIC CHECK (rating BETWEEN 0 AND 5),
    review_count INTEGER NOT NULL DEFAULT 0 CHECK (review_count >= 0),
    in_stock INTEGER NOT NULL DEFAULT 1 CHECK (in_stock IN (0, 1)),
    captured_date TEXT NOT NULL,
    UNIQUE (product_id, retailer_id, captured_date)
);

CREATE INDEX IF NOT EXISTS idx_prices_product_date
    ON price_observations (product_id, captured_date);
CREATE INDEX IF NOT EXISTS idx_prices_retailer
    ON price_observations (retailer_id);
