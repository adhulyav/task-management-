
import sqlite3
from user_auth import create_tables, register, login
from task import task_menu
from admin import admin_login, admin_menu


def main():
    try:
        create_tables()
    except sqlite3.Error as error:
        print("Could not initialize the database:", error)
        return

    print("=" * 40)
    print("      TASK MANAGEMENT SYSTEM")
    print("=" * 40)

    while True:
        print("\nMain Menu")
        print("1. Register")
        print("2. User Login")
        print("3. Admin Login")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            try:
                register()
            except sqlite3.Error as error:
                print("Database error:", error)

        elif choice == "2":
            try:
                user = login()
                if user:
                    task_menu(user)
            except sqlite3.Error as error:
                print("Database error:", error)

        elif choice == "3":
            if admin_login():
                admin_menu()

        elif choice == "4":
            print("Thank you for using the Task Management System!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
