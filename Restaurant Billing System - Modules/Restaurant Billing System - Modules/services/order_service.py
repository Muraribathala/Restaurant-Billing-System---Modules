from database.db_details import connect_database
from services.audit_logs import log_change
from services.menu_service import view_menu, money  # import helpers
from services.staff_service import safe_str_input  # reuse instead of redefining
from datetime import datetime

def view_open_orders():
    conn=connect_database()
    cur=conn.cursor()
    cur.execute("SELECT order_id,table_no,customer_name,total,staff_id FROM orders WHERE status='open'")
    rows=cur.fetchall(); conn.close()
    if not rows:
        print("No open orders.")
        return False
    print("\n----------OPEN ORDERS---------")
    for r in rows:
        print(f"OrderID:{r[0]} | Table:{r[1]} | Customer:{r[2]} | {money(r[3])} | Staff:{r[4]}")
    return True

def take_order(staff_id):
    conn=connect_database()
    cur=conn.cursor()

    print("\n---------TAKIN NEW ORDER------------")

    #Getting valid table number
    while True:
        try:
            table=int(input("Enter Table Number: ").strip())
            if table<=0:
                print("Table number must be a positive integer.")
                continue
        except ValueError:
            print("Invalid input. Please enter a valid table number.")
            continue

        #Check if the table is already occupied
        cur.execute("SELECT COUNT(*) FROM orders WHERE table_no=%s AND status='open'", (table,))
        if cur.fetchone()[0]>0:
            print(f"Table {table} already has an open order. Choose another table.")
        else:
            break

    #Getting customer name
    cname=input("Customer Name: ").strip()
    if not cname:
        print("Customer name cannot be empty.")
        conn.close()
        return

    #Get customer mobile (mandatory, numeric and length check)
    while True:
        cmob=input("Customer Mobile: ").strip()
        if not cmob:
            print("Mobile number is mandatory.")
            continue
        if not cmob.isdigit():
            print("Mobile number must contain only digits.")
            continue
        if len(cmob)!=10:
            print("Mobile number must be 10 digits")
            continue
        break

    #Creating new order
    cur.execute("""
        INSERT INTO orders (table_no, staff_id, customer_name, customer_mobile) 
        VALUES (%s, %s, %s, %s)""", (table, staff_id, cname, cmob))
    conn.commit()
    cur.execute("SELECT LAST_INSERT_ID()")
    oid=cur.fetchone()[0]

    added_items=set()
    print(f"\nNew Order Created (Order ID: {oid}) for Table {table}")

    #Addding items into the orders
    while True:
        view_menu(False)
        try:
            item=int(input("\nEnter Item ID (0 to finish): ").strip())
        except ValueError:
            print("Please enter a valid Item ID number.")
            continue

        if item==0:
            break

        #Validate item availableor not
        cur.execute("SELECT name, stock, price FROM menu WHERE item_id=%s AND available='yes'", (item,))
        row=cur.fetchone()
        if not row:
            print("Invalid or unavailable item.")
            continue

        item_name,stock,price=row

        try:
            qty=int(input(f"Quantity for '{item_name}' (Stock: {stock}): ").strip())
            if qty<=0:
                print("Quantity must be greater than 0.")
                continue
        except ValueError:
            print("Invalid quantity. Please enter a number.")
            continue

        if qty>stock:
            print(f"Only {stock} of '{item_name}' available. Please enter a smaller quantity.")
            continue

        #Add/update order item
        if item in added_items:
            cur.execute("""
            UPDATE order_items SET quantity = quantity + %s WHERE order_id = %s AND item_id = %s
            """, (qty, oid, item))
        else:
            cur.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)
            """, (oid, item, qty, price))
            added_items.add(item)

        #Update stock
        cur.execute("""
            UPDATE menu SET stock = stock - %s, available = IF(stock - %s <= 0, 'no', 'yes') 
            WHERE item_id = %s""", (qty, qty, item))
        conn.commit()

        print(f"Added {qty} * '{item_name}' ({price:.2f}/- each)")

    #Cancel empty order if no items
    cur.execute("SELECT COUNT(*) FROM order_items WHERE order_id=%s", (oid,))
    if cur.fetchone()[0]==0:
        cur.execute("DELETE FROM orders WHERE order_id=%s",(oid,))
        conn.commit()
        conn.close()
        print("Order cancelled — no items added.")
        return

    #Calculate totals
    cur.execute("""
        SELECT SUM(oi.price * oi.quantity), SUM(oi.price * oi.quantity * m.gst_percent / 100)
        FROM order_items oi JOIN menu m ON oi.item_id = m.item_id WHERE oi.order_id = %s
    """, (oid,))
    subtotal,gst=cur.fetchone()
    subtotal,gst=round(subtotal or 0, 2), round(gst or 0, 2)
    total=round(subtotal+gst,2)

    #Update totals
    cur.execute("""UPDATE orders SET subtotal = %s, gst = %s, total = %s WHERE order_id = %s
    """, (subtotal, gst, total, oid))
    conn.commit()
    conn.close()

    print(f"\nOrder {oid} created successfully!")
    print(f"   Customer: {cname} | Mobile: {cmob}")
    print(f"   Subtotal: {subtotal:.2f}/- | GST: {gst:.2f}/- | Total: {total:.2f}/-")

    log_change(staff_id=staff_id, action=f"Created order {oid}", table_name="orders", record_id=str(oid))

def modify_order(staff_id):
    if not view_open_orders():
        return

    conn=connect_database()
    cur=conn.cursor()

    try:
        oid=int(input("\nEnter Order ID to modify: ").strip())
    except ValueError:
        print("Invalid input for Order ID.")
        conn.close()
        return

    cur.execute("SELECT status FROM orders WHERE order_id=%s AND staff_id=%s", (oid, staff_id))
    res=cur.fetchone()
    if not res:
        print("Order not found or not assigned to you.")
        conn.close()
        return
    if res[0]=='closed':
        print("Order already closed. Cannot modify.")
        conn.close()
        return

    print(f"\nEditing Order #{oid} — Use the options below to modify it:")

    while True:
        print("\n1.Add Item")
        print("\n2.Remove Item")
        print("\n3.Change Item Quantity")
        print("\n4.View Current Items")
        print("\n0.Done")

        ch=input("Choice: ").strip()

        if ch=='1':
            view_menu(False)
            try:
                item_id=int(input("Enter Item ID to add: ").strip())
            except ValueError:
                print("Invalid input for Item ID.")
                continue

            cur.execute("SELECT name, stock, price FROM menu WHERE item_id=%s AND available='yes'", (item_id,))
            item=cur.fetchone()
            if not item:
                print("Invalid or unavailable item.")
                continue

            item_name,stock,price=item
            if stock<=0:
                print(f"'{item_name}' is out of stock.")
                continue

            try:
                qty=int(input(f"Quantity for '{item_name}' (Stock: {stock}): ").strip())
                if qty<=0:
                    print("Quantity must be greater than 0.")
                    continue
            except ValueError:
                print("Invalid quantity.")
                continue

            if qty>stock:
                print(f"Only {stock} left in stock. Please reduce quantity.")
                continue

            # Insert or update item in order_items
            cur.execute("SELECT quantity FROM order_items WHERE order_id=%s AND item_id=%s", (oid, item_id))
            exists=cur.fetchone()
            if exists:
                cur.execute("""
                UPDATE order_items SET quantity = quantity + %s WHERE order_id=%s AND item_id=%s
                """, (qty, oid, item_id))
            else:
                cur.execute("""
                INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)
                """, (oid, item_id, qty, price))

            # Deduct stock
            cur.execute("""
                UPDATE menu SET stock = stock - %s, available = IF(stock - %s <= 0, 'no', 'yes')
                WHERE item_id = %s""", (qty, qty, item_id))
            conn.commit()
            print(f"Added {qty} * '{item_name}' to order.")

        elif ch=='2':
            try:
                item_id=int(input("Enter Item ID to remove: ").strip())
            except ValueError:
                print("Invalid input for Item ID.")
                continue

            cur.execute("SELECT quantity FROM order_items WHERE order_id=%s AND item_id=%s", (oid, item_id))
            existing=cur.fetchone()
            if not existing:
                print("This item is not part of the order.")
                continue

            qty=existing[0]

            # Remove from order and restore stock
            cur.execute("DELETE FROM order_items WHERE order_id=%s AND item_id=%s", (oid, item_id))
            cur.execute("""
            UPDATE menu SET stock = stock + %s, available = IF(stock + %s > 0, 'yes', 'no')
            WHERE item_id = %s""", (qty, qty, item_id))
            conn.commit()
            print(f"Removed Item ID {item_id} from order.")

        elif ch=='3':
            try:
                item_id=int(input("Enter Item ID to modify quantity: ").strip())
            except ValueError:
                print("Invalid Item ID.")
                continue

            cur.execute("SELECT quantity FROM order_items WHERE order_id=%s AND item_id=%s", (oid, item_id))
            existing=cur.fetchone()
            if not existing:
                print("This item is not part of the order.")
                continue

            old_qty=existing[0]
            print(f"Current quantity: {old_qty}")

            try:
                new_qty=int(input("Enter new quantity: ").strip())
                if new_qty<=0:
                    print("Quantity must be greater than 0.")
                    continue
            except ValueError:
                print("Invalid input for quantity.")
                continue

            diff=new_qty-old_qty
            # If increasing quantity, check stock
            if diff>0:
                cur.execute("SELECT stock FROM menu WHERE item_id=%s",(item_id,))
                stock=cur.fetchone()[0]
                if diff>stock:
                    print(f"Not enough stock. Only {stock} left.")
                    continue

            # Apply update
            cur.execute("""
            UPDATE order_items SET quantity=%s WHERE order_id=%s AND item_id=%s
            """, (new_qty, oid, item_id))
            cur.execute("""
            UPDATE menu SET stock = stock - %s, available = IF(stock - %s <= 0, 'no', 'yes')
            WHERE item_id=%s""", (diff, diff, item_id))
            conn.commit()
            print(f"Updated Item ID {item_id}: quantity changed from {old_qty} → {new_qty}.")

        elif ch=='4':
            cur.execute("""
            SELECT m.name, oi.quantity, oi.price, (oi.quantity * oi.price) AS total
            FROM order_items oi JOIN menu m ON oi.item_id = m.item_id WHERE oi.order_id = %s""", (oid,))
            rows = cur.fetchall()
            if not rows:
                print("No items in this order yet.")
            else:
                print("\n-----------CURRENT ORDER ITEMS -----------")
                print("Item Name | Quantity | Price | Total")
                print("-" * 50)
                for r in rows:
                    print(f"{r[0]} | {r[1]} | ₹{r[2]:.2f} | ₹{r[3]:.2f}")

        elif ch=='0':
            break
        else:
            print("Invalid choice. Please select a valid option.")

    #Recalculate order totals after modifications
    cur.execute("""
    SELECT SUM(oi.price * oi.quantity), SUM(oi.price * oi.quantity * m.gst_percent / 100)
    FROM order_items oi JOIN menu m ON oi.item_id = m.item_id WHERE oi.order_id = %s""", (oid,))
    subtotal,gst=cur.fetchone()
    subtotal,gst=round(subtotal or 0, 2), round(gst or 0, 2)
    total=round(subtotal + gst, 2)

    cur.execute("""
    UPDATE orders SET subtotal=%s, gst=%s, total=%s WHERE order_id=%s""", (subtotal, gst, total, oid))
    conn.commit()
    conn.close()

    print(f"\nOrder {oid} updated successfully.")
    print(f"   Subtotal: {subtotal:.2f}/- | GST: {gst:.2f}/- | Total: {total:.2f}/-")

    log_change(staff_id=staff_id, action=f"Modified order {oid}", table_name="orders", record_id=str(oid))

def close_order(user_role, staff_id=None):
    if not view_open_orders():
        return

    conn = connect_database()
    cur = conn.cursor()

    try:
        oid=int(input("\nEnter Order ID to close: ").strip())
    except ValueError:
        print("Invalid input for Order ID.")
        conn.close()
        return

    # Verify order validity and ownership (if waiter)
    if user_role=='waiter':
        cur.execute("SELECT status FROM orders WHERE order_id=%s AND staff_id=%s", (oid, staff_id))
    else:
        cur.execute("SELECT status FROM orders WHERE order_id=%s", (oid,))
    result=cur.fetchone()

    if not result:
        print("Order not found or access denied.")
        conn.close()
        return

    status=result[0]

    if status=='closed':
        print("Order already closed.")
        conn.close()
        return

    # Always recalculate live totals
    cur.execute("""
    SELECT SUM(oi.price * oi.quantity), SUM(oi.price * oi.quantity * m.gst_percent / 100)
    FROM order_items oi JOIN menu m ON oi.item_id = m.item_id WHERE oi.order_id = %s""", (oid,))
    subtotal,gst=cur.fetchone()
    subtotal,gst=round(subtotal or 0, 2), round(gst or 0, 2)
    total=round(subtotal + gst, 2)

    # Fetch customer details
    cur.execute("SELECT customer_name, customer_mobile FROM orders WHERE order_id=%s",(oid,))
    customer=cur.fetchone()
    cname,mobile=customer if customer else ("Guest", None)

    # Loyalty discount eligibility
    cur.execute("SELECT COUNT(*) FROM orders WHERE customer_mobile=%s AND status='closed'",(mobile,))
    past_visits=cur.fetchone()[0]
    loyalty_discount=20 if past_visits >= 5 else 0

    # Active discount
    cur.execute("""
    SELECT name, percent FROM discounts WHERE active='yes' AND CURDATE() BETWEEN valid_from AND valid_to
    ORDER BY percent DESC LIMIT 1""")
    discount=cur.fetchone()
    active_name,active_per=(discount if discount else (None, 0))

    if active_per>=loyalty_discount:
        discount_name,discount_per=active_name, active_per
    else:
        discount_name,discount_per="Loyalty Discount",loyalty_discount

    # Fetch table and customer again for preview
    cur.execute("SELECT table_no, customer_name, customer_mobile FROM orders WHERE order_id=%s", (oid,))
    table_no,cname,mobile=cur.fetchone()

    discount_amt=0
    print(f"\n--------BILL PREVIEW----------")
    print(f"Order ID: {oid} | Table: {table_no}")
    print(f"Customer: {cname} | Mobile: {mobile}")
    print("-" * 50)
    print(f"Subtotal: {subtotal:.2f}/-")
    print(f"GST: {gst:.2f}/-")
    print(f"Total (before discount): {total:.2f}/-")

    if discount_per>0:
        print(f"Eligible Discount: {discount_name} ({discount_per}%)")
        discount_amt=round(total * (discount_per / 100), 2)
        print(f"Discount Amount: {discount_amt:.2f}/-")
        print(f"Net Payable (after discount): {total - discount_amt:.2f}/-")
    else:
        print("No active discounts.")

    print("-" * 50)

    # Confirm preview
    if safe_str_input("Proceed to payment? (yes/no): ") != "yes":
        print("Order remains open. You can modify it further before closing.")
        conn.close()
        return

    total-=discount_amt

    # Confirm payment
    print(f"\nFinal Bill for Order {oid}: {total:.2f}/-")
    if safe_str_input("Confirm payment and close order? (yes/no): ") != "yes":
        print("Payment cancelled. Order not closed.")
        conn.close()
        return

    # Payment method input
    while True:
        method=safe_str_input("Payment Method (cash/card/upi): ")
        if method in ("cash","card","upi"):
            break
        print("Invalid method. Choose from cash, card, or upi.")

    # Update order record
    cur.execute("""UPDATE orders SET subtotal=%s, gst=%s, discount=%s, total=%s,
    payment_method=%s, status='closed' WHERE order_id=%s""",(subtotal,gst,discount_amt,total,method,oid))
    conn.commit()
    conn.close()

    print(f"\nOrder {oid} closed successfully!")
    print(f"   Payment Method: {method.upper()} | Amount Paid: {total:.2f}/-")

    # Log action
    if staff_id:
        log_change(staff_id=staff_id, action=f"Closed order {oid}", table_name="orders", record_id=str(oid))
    else:
        log_change(admin_id=staff_id, action=f"Closed order {oid}", table_name="orders", record_id=str(oid))
