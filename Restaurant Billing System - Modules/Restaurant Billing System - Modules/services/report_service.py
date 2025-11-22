from database.db_details import connect_database
import csv
from datetime import datetime

def export_billing_csv(role, staff_id=None):
    conn=connect_database()
    cur=conn.cursor()
    if role=='waiter':
        cur.execute("""SELECT order_id,table_no,customer_name,customer_mobile,subtotal,gst,discount,total,payment_method,created_at
                       FROM orders WHERE status='closed' AND staff_id=%s""",(staff_id,))
    else:
        cur.execute("""SELECT order_id,table_no,customer_name,customer_mobile,subtotal,gst,discount,total,payment_method,created_at
                       FROM orders WHERE status='closed'""")
    rows=cur.fetchall()
    conn.close()
    if not rows:
        print("No bills to export.")
        return
    filename=f"bills_{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(["OrderID","Table","Customer","Mobile","Subtotal","GST","Discount","Total","Payment","Timestamp"])
        w.writerows(rows)
    print(f"Exported to {filename}")

def revenue_report(role='manager'):
    conn=connect_database()
    cur=conn.cursor()

    while True:
        print("\n-----------REVENUE REPORT MENU-----------")

        if role=='manager':
            print("1. Top 10 Most Ordered Dishes")
            print("2. Category-wise Sales Breakdown")
            print("3. Daily Total Sales Report")
            print("4. Monthly Revenue Summary")
            print("5. Average Bill Value per Customer/Table")
            print("6. Peak Hour Sales Analysis")
            print("7. Staff-wise Sales Performance")
            print("8. Total GST Collected (Daily/Monthly)")
            print("9. Coupons/Discount Impact on Revenue")
            print("0. Back")

        elif role=='admin':
            print("1. Top 10 Most Ordered Dishes")
            print("2. Category-wise Sales Breakdown")
            print("3. Daily Total Sales Report")
            print("0. Back")

        choice=input("Select report: ").strip()

        # Manager/Shared Reports
        if choice=='1':
            cur.execute("""
                SELECT m.name AS Item, SUM(oi.quantity) AS Total_Qty, 
                SUM(oi.price * oi.quantity) AS Revenue
                FROM order_items oi
                JOIN menu m ON oi.item_id = m.item_id
                JOIN orders o ON o.order_id = oi.order_id
                WHERE o.status = 'closed' GROUP BY m.name ORDER BY Total_Qty DESC LIMIT 10
            """)
            title="TOP 10 MOST ORDERED DISHES"

        elif choice=='2':
            cur.execute("""
                SELECT m.category, 
                SUM(oi.quantity) AS Total_Items_Sold, SUM(oi.price * oi.quantity) AS Total_Revenue
                FROM order_items oi
                JOIN menu m ON oi.item_id = m.item_id
                JOIN orders o ON o.order_id = oi.order_id
                WHERE o.status = 'closed' GROUP BY m.category ORDER BY Total_Revenue DESC
            """)
            title="CATEGORY-WISE SALES BREAKDOWN"

        elif choice=='3':
            cur.execute("""
                SELECT DATE(o.created_at) AS Date, 
                COUNT(o.order_id) AS Orders, SUM(o.total) AS Total_Sales FROM orders o
                WHERE o.status = 'closed' GROUP BY DATE(o.created_at) ORDER BY Date DESC
            """)
            title="DAILY TOTAL SALES REPORT"

        # Manager-only reports start here
        elif role=='manager' and choice=='4':
            cur.execute("""
                SELECT DATE_FORMAT(o.created_at, '%Y-%m') AS Month,
                COUNT(o.order_id) AS Orders, SUM(o.total) AS Total_Revenue
                FROM orders o WHERE o.status = 'closed' GROUP BY Month ORDER BY Month DESC
            """)
            title="MONTHLY REVENUE SUMMARY"

        elif role=='manager' and choice=='5':
            cur.execute("""
                SELECT 
                ROUND(AVG(o.total), 2) AS Avg_Bill_Per_Order,
                ROUND(SUM(o.total)/COUNT(DISTINCT o.customer_mobile), 2) AS Avg_Per_Customer,
                ROUND(SUM(o.total)/COUNT(DISTINCT o.table_no), 2) AS Avg_Per_Table
                FROM orders o WHERE o.status = 'closed'
            """)
            title="AVERAGE BILL VALUE PER CUSTOMER/TABLE"

        elif role=='manager' and choice=='6':
            cur.execute("""
                SELECT HOUR(o.created_at) AS Hour, 
                COUNT(o.order_id) AS Orders, SUM(o.total) AS Revenue FROM orders o
                WHERE o.status = 'closed' GROUP BY HOUR(o.created_at) ORDER BY Orders DESC
            """)
            title="PEAK HOUR SALES ANALYSIS"

        elif role=='manager' and choice=='7':
            cur.execute("""
                SELECT s.name AS Staff, s.role AS Role,
                COUNT(o.order_id) AS Orders_Handled, SUM(o.total) AS Total_Revenue FROM orders o
                JOIN staff s ON o.staff_id = s.staff_id WHERE o.status = 'closed'
                GROUP BY s.name, s.role ORDER BY Total_Revenue DESC
            """)
            title="STAFF-WISE SALES PERFORMANCE"

        elif role=='manager' and choice=='8':
            print("\nTOTAL GST COLLECTED (DAILY / MONTHLY)")
            sub_choice = input("1. Daily  2. Monthly: ").strip()
            if sub_choice=='1':
                cur.execute("""
                    SELECT DATE(created_at) AS Date, SUM(gst) AS GST_Collected
                    FROM orders WHERE status='closed' GROUP BY DATE(created_at) ORDER BY Date DESC
                """)
                title="DAILY GST COLLECTION"
            elif sub_choice=='2':
                cur.execute("""
                    SELECT DATE_FORMAT(created_at,'%Y-%m') AS Month, SUM(gst) AS GST_Collected
                    FROM orders WHERE status='closed'
                    GROUP BY Month ORDER BY Month DESC
                """)
                title="MONTHLY GST COLLECTION"
            else:
                print("Invalid chooice")

        elif role=='manager' and choice=='9':
            cur.execute("""
                SELECT 
                DATE_FORMAT(o.created_at, '%Y-%m') AS Month,
                COUNT(o.order_id) AS Orders,
                SUM(o.discount) AS Total_Discount,
                SUM(o.total) AS Net_Revenue,
                ROUND(SUM(o.discount) / NULLIF(SUM(o.total + o.discount),0) * 100, 2) AS Discount_Percentage
                FROM orders o
                WHERE o.status='closed' AND o.discount > 0 GROUP BY Month ORDER BY Month DESC
            """)
            title="COUPONS / DISCOUNT IMPACT ON REVENUE"

        elif choice=='0':
            conn.close()
            return
        else:
            print("Invalid option.")
            continue

        rows = cur.fetchall()
        print(f"\n----------{title}-----------")
        if choice=='1':
            print("Item Name | Qty Sold | Revenue")
        elif choice=='2':
            print("Category | Items Sold | Revenue")
        elif choice=='3':
            print("Date | Orders | Total Sales")
        elif choice=='4':
            print("Month | Orders | Revenue")
        elif choice=='5':
            print("Avg/Order | Avg/Customer | Avg/Table")
        elif choice=='6':
            print("Hour | Orders | Revenue")
        elif choice=='7':
            print("Staff | Role | Orders | Revenue")
        elif choice=='8':
            print("Date/Month | GST Collected")
        elif choice=='9':
            print("Month | Orders | Discount | Net Revenue | Discount %")

        if not rows:
            print("No data found.")
        else:
            print("-" * 90)
            for r in rows:
                print(" | ".join(str(x) for x in r))
            print("-" * 90)
