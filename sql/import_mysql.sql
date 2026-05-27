USE market_research;

DROP TEMPORARY TABLE IF EXISTS staging_product_prices;
CREATE TEMPORARY TABLE staging_product_prices (
    product_key VARCHAR(40),
    product_name VARCHAR(180),
    brand VARCHAR(100),
    category VARCHAR(100),
    model_number VARCHAR(80),
    retailer VARCHAR(120),
    listing_reference VARCHAR(80),
    listed_price_inr DECIMAL(10, 2),
    original_price_inr DECIMAL(10, 2),
    rating DECIMAL(2, 1),
    review_count INT,
    in_stock BOOLEAN,
    captured_date DATE
);

-- Change this path to the absolute location of data/product_prices.csv.
LOAD DATA LOCAL INFILE '/absolute/path/to/product_prices.csv'
INTO TABLE staging_product_prices
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

INSERT IGNORE INTO categories (category_name)
SELECT DISTINCT category FROM staging_product_prices;

INSERT IGNORE INTO brands (brand_name)
SELECT DISTINCT brand FROM staging_product_prices;

INSERT IGNORE INTO retailers (retailer_name)
SELECT DISTINCT retailer FROM staging_product_prices;

INSERT INTO products (product_key, product_name, brand_id, category_id, model_number)
SELECT DISTINCT s.product_key, s.product_name, b.brand_id, c.category_id, s.model_number
FROM staging_product_prices s
JOIN brands b ON b.brand_name = s.brand
JOIN categories c ON c.category_name = s.category
ON DUPLICATE KEY UPDATE product_name = VALUES(product_name);

INSERT INTO price_observations (
    product_id, retailer_id, listing_reference, listed_price_inr,
    original_price_inr, rating, review_count, in_stock, captured_date
)
SELECT
    p.product_id, r.retailer_id, s.listing_reference, s.listed_price_inr,
    s.original_price_inr, s.rating, s.review_count, s.in_stock, s.captured_date
FROM staging_product_prices s
JOIN products p ON p.product_key = s.product_key
JOIN retailers r ON r.retailer_name = s.retailer
ON DUPLICATE KEY UPDATE
    listing_reference = VALUES(listing_reference),
    listed_price_inr = VALUES(listed_price_inr),
    original_price_inr = VALUES(original_price_inr),
    rating = VALUES(rating),
    review_count = VALUES(review_count),
    in_stock = VALUES(in_stock);
