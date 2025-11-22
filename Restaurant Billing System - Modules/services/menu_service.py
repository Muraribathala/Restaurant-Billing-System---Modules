from database.db_details import connect_database
from services.audit_logs import log_change

def money(x):
    return f"{x:.2f}/-"

def view_menu(show_inactive=True):
    conn=connect_database()
    cur=conn.cursor()
    query="SELECT item_id,name,category,price,gst_percent,stock,available FROM menu"
    if not show_inactive:
        query+=" WHERE available='yes'"
    cur.execute(query)
    rows=cur.fetchall()
    conn.close()
    print("\n-------------MENU-------------")
    for r in rows:
        warn = "LOW STOCK" if r[5] <= 10 else ""
        print(f"{r[0]} | {r[1]} | {r[2]} | {money(r[3])} | GST {r[4]}% | Stock {r[5]} | {r[6]} {warn}")

def add_menu_item(actor_id,actor_role):
    try:
        name=input("Item Name: ")
        category=input("Category: ")
        price=float(input("Price: "))
        gst=float(input("GST %: "))
        stock=int(input("Stock: "))
    except ValueError:
        print("Invalid input.")
        return
    avail='yes' if stock>0 else 'no'
    conn=connect_database(); cur = conn.cursor()
    cur.execute("INSERT INTO menu (name,category,price,gst_percent,stock,available) VALUES (%s,%s,%s,%s,%s,%s)",
                (name,category,price,gst,stock,avail))
    conn.commit()
    conn.close()
    print("Menu item added.")
    if actor_role=='manager':
        log_change(manager_id=actor_id, action=f"Added menu item {name}", table_name="menu")
    else:
        log_change(admin_id=actor_id, action=f"Added menu item {name}", table_name="menu")

def update_menu_item(actor_id,actor_role):
    view_menu()
    #Get Item ID
    try:
        iid=int(input("\nEnter Item ID to update: ").strip())
    except ValueError:
        print("Invalid input for Item ID.")
        return

    conn=connect_database()
    cur=conn.cursor()

    #Check if item exists
    cur.execute("SELECT name, price, gst_percent, stock, available FROM menu WHERE item_id=%s", (iid,))
    item=cur.fetchone()

    if not item:
        print("Item ID not found.")
        conn.close()
        return

    name, old_price, old_gst, current_stock, available = item
    print(f"\nEditing Item:  {name}")
    print(f"   Current Price: {old_price:.2f}/- | GST: {old_gst}% | Stock: {current_stock} | Available: {available}")

    #Input new values
    try:
        price_input=input(f"New Price [{old_price:.2f}/-]: ").strip()
        gst_input=input(f"New GST % [{old_gst}%]: ").strip()
        stock_input=input("Add Stock (enter 0 if no change): ").strip()

        price=float(price_input) if price_input else old_price
        gst=float(gst_input) if gst_input else old_gst
        added_stock=int(stock_input) if stock_input else 0
    except ValueError:
        print("Invalid numeric input.")
        conn.close()
        return

    new_stock=current_stock + added_stock
    avail='yes' if new_stock > 0 else 'no'

    #Check if anything actually changed
    if price==old_price and gst == old_gst and added_stock == 0:
        print("No changes detected. Nothing updated.")
        conn.close()
        return

    cur.execute("""UPDATE menu SET price=%s, gst_percent=%s, stock=%s, available=%s WHERE item_id=%s
    """, (price, gst, new_stock, avail, iid))
    conn.commit()
    conn.close()

    print(f"\n Menu item '{name}' updated successfully!")
    print(f"   Previous stock: {current_stock}, Added: {added_stock}, New stock: {new_stock}")
    print(f"   Updated Price: {price:.2f}\-, GST: {gst}%")

    if actor_role=='manager':
        log_change(manager_id=actor_id, action=f"Updated menu item {iid} (+{added_stock} stock)", table_name="menu", record_id=str(iid))
    else:
        log_change(admin_id=actor_id, action=f"Updated menu item {iid} (+{added_stock} stock)", table_name="menu", record_id=str(iid))

def deactivate_menu_item(actor_id, actor_role):
    view_menu(False)
    iid=input("Enter Item ID to deactivate: ").strip()
    conn=connect_database()
    cur=conn.cursor()

    #Check if item exists
    cur.execute("SELECT name, available FROM menu WHERE item_id=%s", (iid,))
    item=cur.fetchone()

    if not item:
        print("Item ID not found.")
        conn.close()
        return

    if item[1]=='no':
        print(f"Item '{item[0]}' is already inactive.")
        conn.close()
        return

    #Proceed to deactivate
    cur.execute("UPDATE menu SET available='no' WHERE item_id=%s", (iid,))
    conn.commit()
    conn.close()

    print(f"Item '{item[0]}' deactivated successfully.")
    if actor_role=='manager':
        log_change(manager_id=actor_id, action=f"Deactivated menu item {iid}", table_name="menu", record_id=str(iid))
    else:
        log_change(admin_id=actor_id, action=f"Deactivated menu item {iid}", table_name="menu", record_id=str(iid))

def reactivate_menu_item(actor_id, actor_role):
    conn=connect_database()
    cur=conn.cursor()

    cur.execute("SELECT item_id, name FROM menu WHERE available='no'")
    rows=cur.fetchall()

    if not rows:
        print("No inactive items.")
        conn.close()
        return

    print("\n-----------INACTIVE MENU ITEMS------------")
    for r in rows:
        print(f"{r[0]} | {r[1]}")

    iid=input("Enter Item ID to reactivate: ").strip()

    #Check if item exists
    cur.execute("SELECT name, available, stock FROM menu WHERE item_id=%s", (iid,))
    item=cur.fetchone()

    if not item:
        print("Item ID not found.")
        conn.close()
        return

    if item[1]=='yes':
        print(f"Item '{item[0]}' is already active.")
        conn.close()
        return

    #Proceed to reactivate (only if stock > 0)
    new_status='yes' if item[2] > 0 else 'no'
    cur.execute("UPDATE menu SET available=%s WHERE item_id=%s", (new_status, iid))
    conn.commit()
    conn.close()

    if new_status=='yes':
        print(f"Item '{item[0]}' reactivated successfully.")
    else:
        print(f"Item '{item[0]}' could not be reactivated (out of stock).")

    if actor_role=='manager':
        log_change(manager_id=actor_id, action=f"Reactivated menu item {iid}", table_name="menu", record_id=str(iid))
    else:
        log_change(admin_id=actor_id, action=f"Reactivated menu item {iid}", table_name="menu", record_id=str(iid))
