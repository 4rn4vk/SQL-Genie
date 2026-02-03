-- Sample data for SQL Genie demo

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Insert sample customers
INSERT INTO customers (customer_name, email, country) VALUES
    ('Alice Johnson', 'alice@example.com', 'USA'),
    ('Bob Smith', 'bob@example.com', 'Canada'),
    ('Charlie Brown', 'charlie@example.com', 'UK'),
    ('Diana Prince', 'diana@example.com', 'USA'),
    ('Eve Davis', 'eve@example.com', 'Australia'),
    ('Frank Miller', 'frank@example.com', 'Canada'),
    ('Grace Lee', 'grace@example.com', 'USA'),
    ('Henry Wilson', 'henry@example.com', 'UK'),
    ('Iris Chen', 'iris@example.com', 'USA'),
    ('Jack Taylor', 'jack@example.com', 'Canada');

-- Insert sample orders
INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
    (1, '2024-01-15', 150.00, 'completed'),
    (1, '2024-02-20', 275.50, 'completed'),
    (2, '2024-01-18', 89.99, 'completed'),
    (3, '2024-01-22', 450.00, 'completed'),
    (4, '2024-02-01', 125.75, 'completed'),
    (5, '2024-02-05', 310.00, 'completed'),
    (1, '2024-03-10', 199.99, 'pending'),
    (6, '2024-03-12', 75.50, 'completed'),
    (7, '2024-03-15', 520.00, 'completed'),
    (8, '2024-03-18', 95.00, 'completed'),
    (9, '2024-03-20', 230.00, 'pending'),
    (10, '2024-03-22', 180.00, 'completed'),
    (2, '2024-03-25', 340.00, 'completed'),
    (3, '2024-03-28', 420.00, 'pending');
