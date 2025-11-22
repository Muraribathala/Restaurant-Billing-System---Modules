from services.staff_service import add_staff, view_staff, deactivate_staff, reactivate_staff
from services.menu_service import view_menu, add_menu_item, update_menu_item, deactivate_menu_item, reactivate_menu_item
from services.report_service import revenue_report, export_billing_csv

def admin_dashboard(aid):
    while True:
        print("\n -----------ADMIN PANEL------------")
        print("1.Add Staff 2.View Staff 3.Deactivate Staff 4.Reactivate Staff 5.View Menu 6.Add Menu 7.Update Menu")
        print("8.Deactivate Menu 9.Reactivate Menu 10.Revenue Report 11.Export Bills 0.Logout")
        ch=input("Choice: ")
        if ch=='1': add_staff(aid,'admin')
        elif ch=='2': view_staff()
        elif ch=='3': deactivate_staff(aid,'admin')
        elif ch=='4': reactivate_staff(aid,'admin')
        elif ch=='5': view_menu()
        elif ch=='6': add_menu_item(aid,'admin')
        elif ch=='7': update_menu_item(aid,'admin')
        elif ch=='8': deactivate_menu_item(aid,'admin')
        elif ch=='9': reactivate_menu_item(aid,'admin')
        elif ch=='10': revenue_report('admin')
        elif ch=='11': export_billing_csv('admin')
        elif ch=='0': break
