-- Sample data for SQL Genie demo — DuckDB dialect
-- Load with:  duckdb sql_genie.duckdb < sample_data_duckdb.sql

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    email VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR DEFAULT 'pending'
);

-- Insert sample customers (explicit IDs — DuckDB does not require SERIAL when inserting directly)
INSERT INTO customers VALUES
    (1,  'Alice Johnson', 'alice@example.com',   'USA'),
    (2,  'Bob Smith',     'bob@example.com',     'Canada'),
    (3,  'Charlie Brown', 'charlie@example.com', 'UK'),
    (4,  'Diana Prince',  'diana@example.com',   'USA'),
    (5,  'Eve Davis',     'eve@example.com',     'Australia'),
    (6,  'Frank Miller',  'frank@example.com',   'Canada'),
    (7,  'Grace Lee',     'grace@example.com',   'USA'),
    (8,  'Henry Wilson',  'henry@example.com',   'UK'),
    (9,  'Iris Chen',     'iris@example.com',    'USA'),
    (10, 'Jack Taylor',   'jack@example.com',    'Canada');

-- Insert sample orders
INSERT INTO orders VALUES
    (1,  1, '2024-01-15', 150.00, 'completed'),
    (2,  1, '2024-02-20', 275.50, 'completed'),
    (3,  2, '2024-01-18',  89.99, 'completed'),
    (4,  3, '2024-01-22', 450.00, 'completed'),
    (5,  4, '2024-02-01', 125.75, 'completed'),
    (6,  5, '2024-02-05', 310.00, 'completed'),
    (7,  1, '2024-03-10', 199.99, 'pending'),
    (8,  6, '2024-03-12',  75.50, 'completed'),
    (9,  7, '2024-03-15', 520.00, 'completed'),
    (10, 8, '2024-03-18',  95.00, 'completed'),
    (11, 9, '2024-03-20', 230.00, 'pending'),
    (12,10, '2024-03-22', 180.00, 'completed'),
    (13, 2, '2024-03-25', 340.00, 'completed'),
    (14, 3, '2024-03-28', 420.00, 'pending');
