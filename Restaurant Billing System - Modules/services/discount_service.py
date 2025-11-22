from database.db_details import connect_database
from services.audit_logs import log_change
from datetime import datetime

def _parse_date_input(label, default=None):
    while True:
        raw = input(f"{label}{f' [{default}]' if default else ''}: ").strip()
        if default and raw == "":
            return default
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")

def view_discounts():
    conn = connect_database()
    cur = conn.cursor()
    # Auto-deactivate expired discounts
    cur.execute("""UPDATE discounts SET active='no' WHERE CURDATE() > valid_to AND active='yes'""")
    conn.commit()

    # Get all discounts with status
    cur.execute("""
        SELECT discount_id, name, percent, valid_from, valid_to,
        CASE
            WHEN CURDATE() > valid_to THEN 'expired'
            WHEN CURDATE() < valid_from THEN 'upcoming'
            WHEN active = 'no' THEN 'inactive'
            ELSE 'active'
        END AS status
        FROM discounts
        ORDER BY 
        CASE
            WHEN CURDATE() BETWEEN valid_from AND valid_to AND active='yes' THEN 1
            WHEN CURDATE() BETWEEN valid_from AND valid_to AND active='no' THEN 2
            WHEN CURDATE() < valid_from THEN 3
            ELSE 4
        END, valid_to ASC""")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("\nNo discounts found.")
        return

    print("\n------------DISCOUNTS-----------")
    print("ID | Name | % | Valid From | Valid To | Status")
    print("-" * 70)
    for d_id, name, pct, vfrom, vto, status in rows:
        print(f"{d_id} | {name} | {pct}% | {vfrom} | {vto} | {status}")

def add_discount(manager_id):
    print("\n------ADD DISCOUNT--------")
    name = input("Discount Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    try:
        percent = float(input("Percent (e.g., 10 for 10%): ").strip())
        if percent <= 0 or percent > 100:
            print("Percent must be between 0 and 100.")
            return
    except ValueError:
        print("Invalid percent.")
        return

    valid_from = _parse_date_input("Valid From (YYYY-MM-DD)")
    valid_to = _parse_date_input("Valid To (YYYY-MM-DD)")

    # Convert to dates for validation
    vf_date = datetime.strptime(valid_from, "%Y-%m-%d").date()
    vt_date = datetime.strptime(valid_to, "%Y-%m-%d").date()
    today = datetime.now().date()

    # Date rules
    if vt_date < vf_date:
        print("Valid To cannot be earlier than Valid From.")
        return

    if vt_date < today:
        print("This discount is already expired. Canot add.")
        return

    # Set initial active status
    new_status = 'yes' if vf_date <= today <= vt_date else 'no'

    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO discounts (name, percent, valid_from, valid_to, active)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, percent, valid_from, valid_to, new_status))
    conn.commit()

    # Fetch inserted discount ID
    cur.execute("SELECT LAST_INSERT_ID()")
    discount_id = cur.fetchone()[0]

    conn.close()
    print(f"Discount '{name}' ({percent}%) added successfully ({'ACTIVE' if new_status=='yes' else 'UPCOMING'}).")

    # Log with record_id
    log_change(manager_id=manager_id, action=f"Added discount '{name}'",table_name="discounts", record_id=str(discount_id))


def update_discount(manager_id):
    print("\n--------UPDATE DISCOUNT---------")
    view_discounts()
    try:
        d_id = int(input("\nEnter Discount ID to update: ").strip())
    except ValueError:
        print("Invalid Discount ID.")
        return

    conn = connect_database()
    cur = conn.cursor()

    # Fetch existing discount
    cur.execute("SELECT name, percent, valid_from, valid_to FROM discounts WHERE discount_id=%s", (d_id,))
    row = cur.fetchone()

    if not row:
        print("Discount not found.")
        conn.close()
        return

    old_name, old_percent, old_from, old_to = row

    print(f"\nEditing: {old_name} | {old_percent}% | {old_from} → {old_to}")

    # Get Name
    name = input(f"New Name [{old_name}]: ").strip() or old_name

    # Get Percent
    try:
        p_in = input(f"New Percent [{old_percent}%]: ").strip()
        percent = float(p_in) if p_in else float(old_percent)
        if percent <= 0 or percent > 100:
            print("Percent must be between 0 and 100.")
            conn.close()
            return
    except ValueError:
        print("Invalid percent.")
        conn.close()
        return

    # Get Dates (string or enter-to-keep-old)
    valid_from = _parse_date_input("New Valid From (YYYY-MM-DD)", default=old_from)
    valid_to = _parse_date_input("New Valid To (YYYY-MM-DD)", default=old_to)

    # Normalize date types (convert strings to date)
    vf_date = datetime.strptime(valid_from, "%Y-%m-%d").date() if isinstance(valid_from, str) else valid_from
    vt_date = datetime.strptime(valid_to, "%Y-%m-%d").date() if isinstance(valid_to, str) else valid_to

    # Validate date range
    if vt_date < vf_date:
        print("Valid To cannot be earlier than Valid From.")
        conn.close()
        return

    # Update discount
    cur.execute("""
        UPDATE discounts 
        SET name=%s, percent=%s, valid_from=%s, valid_to=%s 
        WHERE discount_id=%s
    """, (name, percent, vf_date, vt_date, d_id))

    conn.commit()
    conn.close()

    print("Discount updated successfully.")
    log_change(manager_id=manager_id, action=f"Updated discount {d_id}", table_name="discounts", record_id=str(d_id))


def toggle_discount_status(manager_id):
    print("\n-------TOGGLE DISCOUNT STATUS (ON/OFF)------")
    view_discounts()

    try:
        d_id = int(input("\nEnter Discount ID to toggle: ").strip())
    except ValueError:
        print("Invalid Discount ID.")
        return

    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""
        SELECT active, valid_from, valid_to FROM discounts WHERE discount_id=%s""", (d_id,))
    row = cur.fetchone()

    if not row:
        print("Discount not found.")
        conn.close()
        return

    current_status, valid_from, valid_to = row
    today = datetime.now().date()

    # Block expired
    if valid_to < today:
        print("This discount has expired and cannot be toggled.")
        conn.close()
        return

    # Block upcoming
    if valid_from > today:
        print("This discount has not started yet (UPCOMING). Cannot toggle.")
        conn.close()
        return

    # Toggle only if active in valid date range
    new_status = 'no' if current_status == 'yes' else 'yes'
    cur.execute("UPDATE discounts SET active=%s WHERE discount_id=%s", (new_status, d_id))
    conn.commit()
    conn.close()

    print(f"Discount {d_id} is now {'ACTIVE' if new_status == 'yes' else 'INACTIVE'}.")
    log_change(manager_id=manager_id, action=f"Toggled discount {d_id}", table_name="discounts", record_id=str(d_id))

