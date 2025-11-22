from database.db_details import connect_database
from services.audit_logs import log_change

def safe_str_input(prompt):
    return input(prompt).strip().lower()

def generate_admin_id():
    conn=connect_database()
    cur=conn.cursor()
    cur.execute("SELECT admin_id FROM admin ORDER BY admin_id DESC LIMIT 1")
    res=cur.fetchone()
    conn.close()
    return "Hydadmin001" if not res else f"Hydadmin{int(res[0][8:])+1:03d}"

def generate_staff_id():
    conn=connect_database()
    cur=conn.cursor()
    cur.execute("SELECT staff_id FROM staff ORDER BY staff_id DESC LIMIT 1")
    res=cur.fetchone()
    conn.close()
    return "Hyd0001" if not res else f"Hyd{int(res[0][3:])+1:04d}"

def add_admin(manager_id):
    name = input("Admin Name: ")
    username = input("Username: ")
    password = input("Password: ")
    aid = generate_admin_id()
    conn = connect_database(); cur = conn.cursor()
    cur.execute("INSERT INTO admin (admin_id,name,username,password) VALUES (%s,%s,%s,%s)",
                (aid,name,username,password))
    conn.commit(); conn.close()
    print(f"Admin added: {name}")
    log_change(manager_id=manager_id, action=f"Added admin {name}", table_name="admin", record_id=aid)

def add_staff(actor_id, actor_role):
    name = input("Staff Name: ")
    username = input("Username: ")
    password = input("Password: ")
    role = safe_str_input("Role (waiter/cashier): ")
    if role not in ["waiter", "cashier"]:
        print("Invalid role.")
        return
    sid = generate_staff_id()
    conn = connect_database(); cur = conn.cursor()
    cur.execute("INSERT INTO staff (staff_id,name,username,password,role,status) VALUES (%s,%s,%s,%s,%s,%s)",
                (sid,name,username,password,role,'active'))
    conn.commit(); conn.close()
    print(f"Added {role}: {name}")
    if actor_role == 'manager':
        log_change(manager_id=actor_id, action=f"Added staff {name}", table_name="staff", record_id=sid)
    else:
        log_change(admin_id=actor_id, action=f"Added staff {name}", table_name="staff", record_id=sid)

def view_admins():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT admin_id, name, username FROM admin")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No admins found.")
        return
    print("\n-----------ADMIN LIST------------")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]}")

def view_staff():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT staff_id,name,role,status FROM staff")
    rows = cur.fetchall()
    conn.close()
    print("\n------------STAFF LIST-----------")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")

def deactivate_staff(actor_id, actor_role):
    view_staff()
    sid = input("Enter Staff ID to deactivate: ").strip()
    conn = connect_database()
    cur = conn.cursor()

    #Check if staff exists
    cur.execute("SELECT name, status FROM staff WHERE staff_id=%s", (sid,))
    staff = cur.fetchone()

    if not staff:
        print("Staff ID not found.")
        conn.close()
        return

    if staff[1] == 'inactive':
        print(f"Staff '{staff[0]}' is already inactive.")
        conn.close()
        return

    #Proceed to deactivate
    cur.execute("UPDATE staff SET status='inactive' WHERE staff_id=%s", (sid,))
    conn.commit()
    conn.close()

    print(f"Staff '{staff[0]}' deactivated successfully.")
    if actor_role == 'manager':
        log_change(manager_id=actor_id, action=f"Deactivated staff {sid}", table_name="staff", record_id=sid)
    else:
        log_change(admin_id=actor_id, action=f"Deactivated staff {sid}", table_name="staff", record_id=sid)

def reactivate_staff(actor_id, actor_role):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("SELECT staff_id, name FROM staff WHERE status='inactive'")
    rows = cur.fetchall()

    if not rows:
        print("No inactive staff.")
        conn.close()
        return

    print("\n----------INACTIVE STAFF---------")
    for r in rows:
        print(f"{r[0]} | {r[1]}")

    sid = input("Enter Staff ID to reactivate: ").strip()

    #Check if staff exists and is inactive
    cur.execute("SELECT name, status FROM staff WHERE staff_id=%s", (sid,))
    staff = cur.fetchone()

    if not staff:
        print("Staff ID not found.")
        conn.close()
        return

    if staff[1] == 'active':
        print(f"Staff '{staff[0]}' is already active.")
        conn.close()
        return

    #To reactivate
    cur.execute("UPDATE staff SET status='active' WHERE staff_id=%s", (sid,))
    conn.commit()
    conn.close()

    print(f"Staff '{staff[0]}' reactivated successfully.")
    if actor_role == 'manager':
        log_change(manager_id=actor_id, action=f"Reactivated staff {sid}", table_name="staff", record_id=sid)
    else:
        log_change(admin_id=actor_id, action=f"Reactivated staff {sid}", table_name="staff", record_id=sid)

