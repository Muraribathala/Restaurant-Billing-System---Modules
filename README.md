# Restaurant-Billing-System---Modules
🍽️ Restaurant Ordering & Billing System

A complete Restaurant POS (Point of Sale) built using Python and MySQL, designed to automate ordering, billing, discount handling, user roles, and sales analytics.

📌 Overview

This project is a fully functional Restaurant Ordering & Billing System that digitalizes restaurant operations. The system supports multiple roles, manages menu and staff, handles orders, generates bills with GST & discounts, and produces analytical sales reports.

It is structured to simulate a real-world restaurant billing/POS environment using strong database relationships, logs, and reporting tools.

🚀 Features
👤 User Roles & Dashboards

Manager

Manage menu, staff, discounts, taxes

View audit logs

View daily/monthly/category-wise insights

Admin

Add/manage users

Export data

View revenue & order reports

Waiter

Take new orders

Modify existing orders

Cashier

Process payments (Cash/Card/UPI)

Generate final bill

🧾 Ordering & Billing

Create and edit customer orders

Itemized billing

Auto GST calculation

Discount application (Festival/Weekend/Custom)

Payment processing

Order status tracking (“open/closed”)

📊 Reports & Analytics

Top 10 selling dishes

Category-wise sales

Daily revenue

Monthly revenue summary

Staff-wise performance

Export report as CSV

🛠️ Tech Stack
Component	Technology Used
Programming Language	Python
Database	MySQL
Interface	CLI / Terminal
File Export	CSV
Data Integrity	Relational Keys + Audit Logs
🗂️ Database Structure (Important Tables)
👇 Core Tables

menu – stores dish info

orders – stores order headers

order_items – individual food items under an order

discounts – active/inactive discount rules

staff – waiter/cashier data

admin / manager – privileged user accounts

change_logs – tracks all actions for accountability

The project uses a normalized relational schema for scalability and accuracy.

📐 ER Diagram

The ER diagram defines relationships between Menu, Orders, Order Items, Staff, Managers/Admin, and Change Logs, ensuring clean relational mapping and strong data integrity.

(Include your ERD image here if adding to GitHub.)

📚 SQL Scripts

The project includes complete SQL scripts for:

Table Creation

Insert Data

Select Queries

Update Queries

Advanced reports using JOIN, GROUP BY, HAVING

These scripts help set up the database quickly and run analytics on sales and performance.

▶️ How to Run the Project
1. Install Dependencies
pip install mysql-connector-python

2. Import SQL Database

Run all SQL scripts in MySQL Workbench or any MySQL interface.

3. Update Database Credentials

In your Python file:

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your-password",
    database="restaurant_db"
)

4. Run the Application
python main.py

📦 Folder Structure (Recommended)
Restaurant-Ordering-Billing/
│── main.py
│── database/
│     ├── create_tables.sql
│     ├── insert_data.sql
│── assets/
│     ├── ERD.png
│── README.md

📄 License

This project is open-source and free to modify for personal or academic use.
