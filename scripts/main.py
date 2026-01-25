import json
expenses = []
def load_expenses():
    global expenses
    try:
        with open("expenses.json", "r") as file:
            expenses = json.load(file)
    except FileNotFoundError:
        expenses = []

def save_expenses():
    with open("expenses.json", "w") as file:
        json.dump(expenses, file)
def add_expense():
    while True:
        try:
            amount = float(input("Enter amount: "))
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")

    while True:
        category = input("Enter category: ").strip() 
        if all(x.isalpha() or x.isspace() for x in category) and category != "":
            break
        else:
            print("Invalid category. Only letters allowed.")
    expense = {
        "amount": amount,
        "category": category
    }
    expenses.append(expense)
    save_expenses()  
    print("Expense added successfully!")


def view_expenses():
    if not expenses:
        print("No expenses found.")
        return

    for i, expense in enumerate(expenses, start=1):
        print(f"{i}. {expense['category']} - ₹{expense['amount']}")
def delete_expense():
    view_expenses()
    try:
        idx = int(input("Enter expense number to delete: ")) - 1
        if 0 <= idx < len(expenses) :
            removed = expenses.pop(idx)
            save_expenses()
            print(f"Deleted {removed['category']} - ₹{removed['amount']}")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a number.")

def main():
    load_expenses()
    while True:
        print("\n1. Add Expense")
        print("2. View Expenses")
        print("3. Exit")
        print("4.Delete Expense")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            print("good bye")
            break
        elif choice=="4":
            delete_expense()
        
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()

    
