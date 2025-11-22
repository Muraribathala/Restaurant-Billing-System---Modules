CREATE DATABASE RestaurantBillingSystem;
USE RestaurantBillingSystem;

CREATE TABLE manager (
manager_id VARCHAR(20) PRIMARY KEY,
name VARCHAR(50) NOT NULL,
username VARCHAR(30) UNIQUE NOT NULL,
password VARCHAR(50) NOT NULL,
created_by VARCHAR(20)
);

CREATE TABLE admin (
admin_id VARCHAR(20) PRIMARY KEY,
name VARCHAR(50) NOT NULL,
username VARCHAR(30) UNIQUE NOT NULL,
password VARCHAR(50) NOT NULL
);

CREATE TABLE staff (
staff_id VARCHAR(20) PRIMARY KEY,
name VARCHAR(50) NOT NULL,
username VARCHAR(30) UNIQUE NOT NULL,
password VARCHAR(50) NOT NULL,
role ENUM('waiter','cashier') NOT NULL,
status ENUM('active','inactive') DEFAULT 'active'
);

CREATE TABLE menu (
item_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(50) NOT NULL,
category VARCHAR(30) NOT NULL,
price DECIMAL(10,2) NOT NULL,
gst_percent DECIMAL(5,2) NOT NULL,
stock INT DEFAULT 0,
available ENUM('yes','no') DEFAULT 'yes'
) AUTO_INCREMENT=101;

CREATE TABLE discounts (
discount_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(50) NOT NULL,
percent DECIMAL(5,2) NOT NULL,
valid_from DATE NOT NULL,
valid_to DATE NOT NULL,
active ENUM('yes','no') DEFAULT 'yes'
) AUTO_INCREMENT=10101;

CREATE TABLE orders (
order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
table_no INT NOT NULL,
staff_id VARCHAR(20),
customer_name VARCHAR(100),
customer_mobile VARCHAR(15) NOT NULL,
subtotal DECIMAL(10,2) DEFAULT 0,
gst DECIMAL(10,2) DEFAULT 0,
discount DECIMAL(10,2) DEFAULT 0,
total DECIMAL(10,2) DEFAULT 0,
status ENUM('open','closed') DEFAULT 'open',
payment_method VARCHAR(20),
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) AUTO_INCREMENT=202500001;

CREATE TABLE order_items (
order_item_id INT AUTO_INCREMENT PRIMARY KEY,
order_id BIGINT,
item_id INT,
quantity INT NOT NULL,
price DECIMAL(10,2) NOT NULL,
FOREIGN KEY (order_id) REFERENCES orders(order_id),
FOREIGN KEY (item_id) REFERENCES menu(item_id)
);

CREATE TABLE change_logs (
log_id INT AUTO_INCREMENT PRIMARY KEY,
manager_id VARCHAR(20),
admin_id VARCHAR(20),
staff_id VARCHAR(20),
action TEXT NOT NULL,
table_name VARCHAR(50) NOT NULL,
record_id VARCHAR(20),
changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO manager (manager_id, name, username, password, created_by) VALUES
('Hydmanager001', 'Mithun', 'mithun', 'mithun123', NULL);

INSERT INTO admin (admin_id, name, username, password) VALUES
('Hydadmin001', 'Vishu', 'vishu', 'vishu123'),
('Hydadmin002', 'Divya', 'divya', 'divya123');

INSERT INTO staff (staff_id, name, username, password, role, status) VALUES
('Hyd0001', 'Chandu', 'chandu', 'chandu123', 'waiter', 'active'),
('Hyd0002', 'Vinay', 'vinay', 'vinay123', 'cashier', 'active'),
('Hyd0003', 'Sai', 'sai', 'sai123', 'waiter', 'active'),
('Hyd0004', 'Varun', 'varun', 'varun123', 'cashier', 'active'),
('Hyd0005', 'Divya', 'divya', 'divya123', 'waiter', 'inactive');

INSERT INTO menu (name, category, price, gst_percent, stock, available) VALUES
('Paneer Butter Masala', 'Main Course', 250.00, 5.00, 20, 'yes'),
('Veg Biryani', 'Main Course', 180.00, 5.00, 15, 'yes'),
('Gulab Jamun', 'Desserts', 60.00, 5.00, 30, 'yes'),
('Cold Coffee', 'Beverages', 90.00, 5.00, 3, 'yes'),
('French Fries', 'Starters', 120.00, 5.00, 10, 'yes'),
('Chicken Curry', 'Main Course', 300.00, 5.00, 8, 'yes');

INSERT INTO discounts (name, percent, valid_from, valid_to, active) VALUES
('Weekend Offer', 10.00, '2025-01-01', '2025-12-31', 'yes'),
('Festive Special', 15.00, '2025-10-01', '2025-10-31', 'yes'),
('New Year Blast', 25.00, '2025-12-25', '2026-01-05', 'yes'),
('Summer Delight', 5.00, '2025-04-01', '2025-06-30', 'no');
