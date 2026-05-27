CREATE DATABASE IF NOT EXISTS market_research;
USE market_research;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS retailers (
    retailer_id INT AUTO_INCREMENT PRIMARY KEY,
    retailer_name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_key VARCHAR(40) NOT NULL UNIQUE,
    product_name VARCHAR(180) NOT NULL,
    brand_id INT NOT NULL,
    category_id INT NOT NULL,
    model_number VARCHAR(80) NOT NULL,
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(category_id),
    CONSTRAINT uq_product_model UNIQUE (brand_id, model_number)
);

CREATE TABLE IF NOT EXISTS price_observations (
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    retailer_id INT NOT NULL,
    listing_reference VARCHAR(80) NOT NULL,
    listed_price_inr DECIMAL(10, 2) NOT NULL,
    original_price_inr DECIMAL(10, 2) NOT NULL,
    rating DECIMAL(2, 1),
    review_count INT NOT NULL DEFAULT 0,
    in_stock BOOLEAN NOT NULL DEFAULT TRUE,
    captured_date DATE NOT NULL,
    CONSTRAINT chk_listed_price CHECK (listed_price_inr > 0),
    CONSTRAINT chk_original_price CHECK (original_price_inr >= listed_price_inr),
    CONSTRAINT chk_rating CHECK (rating BETWEEN 0 AND 5),
    CONSTRAINT chk_reviews CHECK (review_count >= 0),
    CONSTRAINT fk_price_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_price_retailer FOREIGN KEY (retailer_id) REFERENCES retailers(retailer_id),
    CONSTRAINT uq_price_observation UNIQUE (product_id, retailer_id, captured_date)
);

CREATE INDEX idx_prices_product_date ON price_observations (product_id, captured_date);
CREATE INDEX idx_prices_retailer ON price_observations (retailer_id);
