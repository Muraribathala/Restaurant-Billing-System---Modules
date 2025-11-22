from database.db_details import connect_database
from controllers.manager_dashboard import manager_dashboard
from controllers.admin_dashboard import admin_dashboard
from controllers.waiter_dashboard import waiter_dashboard
from controllers.cashier_dashboard import cashier_dashboard

def login():
    while True:
        print("\n1.Manager Login  \n2.Admin Login  \n3.Staff Login  \n4.Exit")
        c=input("Choice: ")
        if c=='1':
            u=input("Username: ")
            p=input("Password: ")
            conn=connect_database(); cur=conn.cursor()
            cur.execute("SELECT manager_id,name FROM manager WHERE username=%s AND password=%s",(u,p))
            r=cur.fetchone()
            conn.close()
            if r: 
                print(f"Welcome Manager {r[1]}!")
                manager_dashboard(r[0])
            else: 
                print("Invalid credentials.")
        elif c=='2':
            u=input("Username: ")
            p=input("Password: ")
            conn=connect_database()
            cur=conn.cursor()
            cur.execute("SELECT admin_id,name FROM admin WHERE username=%s AND password=%s",(u,p))
            r=cur.fetchone()
            conn.close()
            if r: 
                print(f"Welcome Admin {r[1]}!")
                admin_dashboard(r[0])
            else: 
                print("Invalid credentials.")
        elif c=='3':
            u=input("Username: ")
            p=input("Password: ")
            conn=connect_database()
            cur=conn.cursor()
            cur.execute("SELECT staff_id,name,role FROM staff WHERE username=%s AND password=%s AND status='active'",(u,p))
            r=cur.fetchone()
            conn.close()
            if r:
                print(f"Welcome {r[1]} ({r[2]})")
                if r[2]=='waiter': 
                    waiter_dashboard(r[0])
                else: 
                    cashier_dashboard(r[0])
            else: print("Invalid or inactive staff.")
        elif c=='4':
            break
        else: 
            print("Invalid choice")
