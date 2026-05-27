-- CREATE: insert a new retailer price observation for an existing product.
INSERT OR IGNORE INTO retailers (retailer_name) VALUES ('Demo Electronics');

INSERT INTO price_observations (
    product_id, retailer_id, listing_reference, listed_price_inr,
    original_price_inr, rating, review_count, in_stock, captured_date
)
SELECT
    p.product_id, r.retailer_id, 'DEMO-M331', 859.00,
    1295.00, 4.3, 25, 1, '2026-05-21'
FROM products p
CROSS JOIN retailers r
WHERE p.product_key = 'LOG-M331'
  AND r.retailer_name = 'Demo Electronics';

-- READ: compare in-stock prices and calculate discount.
SELECT
    p.product_name,
    r.retailer_name,
    po.listed_price_inr,
    ROUND((po.original_price_inr - po.listed_price_inr)
          * 100.0 / po.original_price_inr, 2) AS discount_percent
FROM price_observations po
JOIN products p ON p.product_id = po.product_id
JOIN retailers r ON r.retailer_id = po.retailer_id
WHERE p.product_key = 'LOG-M331' AND po.in_stock = 1
ORDER BY po.listed_price_inr;

-- UPDATE: record a new promotional price.
UPDATE price_observations
SET listed_price_inr = 829.00,
    captured_date = '2026-05-22'
WHERE listing_reference = 'DEMO-M331';

-- DELETE: remove the classroom/demo listing.
DELETE FROM price_observations
WHERE listing_reference = 'DEMO-M331';

-- REPORT: cheapest available retailer and possible saving per product.
WITH ranked AS (
    SELECT
        p.product_name,
        r.retailer_name,
        po.listed_price_inr,
        ROW_NUMBER() OVER (
            PARTITION BY p.product_id ORDER BY po.listed_price_inr
        ) AS price_rank,
        MAX(po.listed_price_inr) OVER (PARTITION BY p.product_id) AS highest_price
    FROM price_observations po
    JOIN products p ON p.product_id = po.product_id
    JOIN retailers r ON r.retailer_id = po.retailer_id
    WHERE po.in_stock = 1
)
SELECT product_name, retailer_name AS cheapest_retailer, listed_price_inr AS lowest_price,
       highest_price, highest_price - listed_price_inr AS possible_saving
FROM ranked
WHERE price_rank = 1
ORDER BY possible_saving DESC;
