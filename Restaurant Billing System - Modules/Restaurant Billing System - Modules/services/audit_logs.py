from database.db_details import connect_database

def log_change(manager_id=None, admin_id=None, staff_id=None, action=None, table_name=None, record_id=None):
    conn=connect_database()
    cur=conn.cursor()
    cur.execute("""
        INSERT INTO change_logs (manager_id, admin_id, staff_id, action, table_name, record_id)
        VALUES (%s,%s,%s,%s,%s,%s)""", (manager_id, admin_id, staff_id, action, table_name, record_id))
    conn.commit()
    conn.close()

def view_audit_trail():
    conn=connect_database()
    cur=conn.cursor()

    print("\n-------AUDIT TRAIL FILTER---------")
    print("\n1.All Logs")
    print("\n2.Only Manager Actions")
    print("\n3.Only Admin Actions")
    print("\n4.Only Staff Actions")
    choice=input("Select filter (1-4): ").strip()

    role_filter=None
    if choice=='2':
        role_filter='manager'
    elif choice=='3':
        role_filter='admin'
    elif choice=='4':
        role_filter='staff'

    # Optional date filter
    use_date_filter=input("Filter by date range? (yes/no): ").strip().lower()
    date_from=date_to=None
    if use_date_filter=='yes':
        date_from=input("From date (YYYY-MM-DD): ").strip()
        date_to=input("To date (YYYY-MM-DD): ").strip()

    where_clauses=[]
    params=[]

    if role_filter=='manager':
        where_clauses.append("c.manager_id IS NOT NULL")
    elif role_filter=='admin':
        where_clauses.append("c.admin_id IS NOT NULL")
    elif role_filter=='staff':
        where_clauses.append("c.staff_id IS NOT NULL")

    if date_from and date_to:
        where_clauses.append("DATE(c.changed_at) BETWEEN %s AND %s")
        params.extend([date_from,date_to])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
            SELECT 
            COALESCE(m.manager_id, a.admin_id, s.staff_id, 'N/A') AS user_id,
            COALESCE(m.name, a.name, s.name, 'Unknown') AS user_name,
            CASE
            WHEN m.manager_id IS NOT NULL THEN 'Manager'
            WHEN a.admin_id IS NOT NULL THEN 'Admin'
            WHEN s.staff_id IS NOT NULL THEN 'Staff'
            ELSE 'Unknown'
            END AS role,
            c.table_name, c.record_id, c.action, c.changed_at 
            FROM change_logs c 
            LEFT JOIN manager m ON c.manager_id = m.manager_id 
            LEFT JOIN admin a ON c.admin_id = a.admin_id
            LEFT JOIN staff s ON c.staff_id = s.staff_id
            {where_sql} ORDER BY c.changed_at DESC LIMIT 200
            """

    cur.execute(query, params)
    rows=cur.fetchall()
    conn.close()

    if not rows:
        print("\nNo audit logs found for the selected filter.")
        return

    print("\n-------------AUDIT TRAIL--------------")
    print("Timestamp | User (ID) | Role | Table | Record | Action")
    print("-" * 100)
    for user_id, user_name, role, table, record, action, ts in rows:
        print(f"[{ts}] {user_name} ({user_id}) | {role} | {table} | {record} | {action}")