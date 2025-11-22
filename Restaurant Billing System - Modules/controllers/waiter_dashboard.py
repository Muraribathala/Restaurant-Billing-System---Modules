from services.order_service import take_order, modify_order, close_order
from services.report_service import export_billing_csv
from services.menu_service import view_menu

def waiter_dashboard(sid):
    while True:
        print("\n------------------WAITER PANEL--------------------")
        print("1.Take Order \n2.Modify Order \n3.Close Order \n4.Export Bills \n5.View Menu \n0.Logout")
        ch=input("Choice: ")
        if ch=='1': take_order(sid)
        elif ch=='2': modify_order(sid)
        elif ch=='3': close_order('waiter',sid)
        elif ch=='4': export_billing_csv('waiter',sid)
        elif ch=='5': view_menu(False)
        elif ch=='0': break
