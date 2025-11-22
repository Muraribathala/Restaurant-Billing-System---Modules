from services.discount_service import view_discounts, add_discount, update_discount, toggle_discount_status
def discount_dashboard(manager_id):
    while True:
        print("\n-----------DISCOUNT MANAGEMENT---------")
        print("1.View Discounts  2.Add Discount  3.Update Discount  4.Toggle Discount Status  0.Back")
        ch = input("Choice: ").strip()
        if ch == '1': view_discounts()
        elif ch == '2': add_discount(manager_id)
        elif ch == '3': update_discount(manager_id)
        elif ch == '4': toggle_discount_status(manager_id)
        elif ch == '0': break
        else: print("Invalid choice.")
        