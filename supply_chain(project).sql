CREATE DATABASE supply_chain;
USE supply_chain;

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    stock_quantity INT,
    reorder_level INT,
    warehouse_location VARCHAR(50),
    unit_price DECIMAL(10,2)
);

CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY,
    supplier_name VARCHAR(100),
    country VARCHAR(50),
    reliability_score FLOAT
);

CREATE TABLE shipments (
    shipment_id INT PRIMARY KEY,
    supplier_id INT,
    product_id INT,
    shipment_date DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    quantity INT,
    transport_cost DECIMAL(10,2),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE sales (
    sale_id INT PRIMARY KEY,
    product_id INT,
    sale_date DATE,
    quantity_sold INT,
    revenue DECIMAL(10,2),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

SELECT product_id,
SUM(quantity_sold) AS total_sales
FROM sales
GROUP BY product_id
ORDER BY total_sales DESC
LIMIT 5;

SELECT AVG(reliability_score)
FROM suppliers;

SELECT shipment_id,
DATEDIFF(actual_delivery, expected_delivery) AS delay_days
FROM shipments
WHERE actual_delivery > expected_delivery;






