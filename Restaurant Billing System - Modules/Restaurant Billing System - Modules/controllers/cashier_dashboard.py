from services.order_service import close_order
from services.report_service import export_billing_csv

def cashier_dashboard(sid):
    while True:
        print("\n-------- CASHIER PANEL ------------")
        print("1.Close Order 2.Export Bills 0.Logout")
        ch=input("Choice: ")
        if ch=='1': close_order('cashier',sid)
        elif ch=='2': export_billing_csv('cashier')
        elif ch=='0': break
