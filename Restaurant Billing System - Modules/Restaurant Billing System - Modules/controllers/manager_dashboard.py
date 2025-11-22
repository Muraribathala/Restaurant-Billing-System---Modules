from services.staff_service import add_staff, view_staff, deactivate_staff, reactivate_staff, add_admin, view_admins
from services.menu_service import view_menu
from services.report_service import revenue_report, export_billing_csv
from services.audit_logs import view_audit_trail
from controllers.discount_dashboard import discount_dashboard

def manager_dashboard(mid):
    while True:
        print("\n -----------------MANAGER PANEL------------------")
        print("1.Add Admin 2.Add Staff 3.View Staff 4.View Admins 5.Deactivate Staff 6.Reactivate Staff")
        print("7.Revenue Report 8.Export Bills 9.Audit Trails 10.Manage Discounts 0.Logout")
        ch = input("Choice: ")

        if ch=='1': add_admin(mid)
        elif ch=='2': add_staff(mid,'manager')
        elif ch=='3': view_staff()
        elif ch=='4': view_admins()
        elif ch=='5': deactivate_staff(mid,'manager')
        elif ch=='6': reactivate_staff(mid,'manager')
        elif ch=='7': revenue_report('manager')
        elif ch=='8': export_billing_csv('manager')
        elif ch=='9': view_audit_trail()
        elif ch=='10': discount_dashboard(mid)
        elif ch=='0': break
        else: print("Invalid choice")
