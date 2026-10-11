import sqlite3

DB_NAME = "task_management.db"


def admin_login():
    print("\n--- Admin Login ---")

    email = input("Enter admin email: ").strip().lower()
    password = input("Enter admin password: ")

    if email == "admin@gmail.com" and password == "admin123":
        print("\nAdmin login successful!")
        return True

    print("Invalid admin email or password.")
    return False

def admin_dashboard():
    print("\n========== ADMIN DASHBOARD ==========")

    with sqlite3.connect(DB_NAME) as conn:

        # Total users
        total_users = conn.execute(
            "SELECT COUNT(*) FROM Users"
        ).fetchone()[0]

        # Total tasks
        total_tasks = conn.execute(
            "SELECT COUNT(*) FROM Tasks"
        ).fetchone()[0]

        # Completed tasks
        completed_tasks = conn.execute(
            "SELECT COUNT(*) FROM Tasks WHERE status = 'Completed'"
        ).fetchone()[0]

        # Pending tasks
        pending_tasks = conn.execute(
            "SELECT COUNT(*) FROM Tasks WHERE status = 'Pending'"
        ).fetchone()[0]

        # In Progress tasks
        in_progress_tasks = conn.execute(

            "SELECT COUNT(*) FROM Tasks WHERE status = 'In Progress'"
        ).fetchone()[0]

    print(f"Total Users       : {total_users}")
    print(f"Total Tasks       : {total_tasks}")
    print(f"Completed Tasks   : {completed_tasks}")
    print(f"Pending Tasks     : {pending_tasks}")
    print(f"In Progress Tasks : {in_progress_tasks}")

    print("====================================")


def view_user_progress():
    print("\n========== USER PROGRESS ==========")

    with sqlite3.connect(DB_NAME) as conn:

        users = conn.execute("""
            SELECT user_id, name
            FROM Users
            ORDER BY name
        """).fetchall()

        for user_id, name in users:

            total = conn.execute("""
                SELECT COUNT(*)
                FROM Tasks
                WHERE user_id = ?
            """, (user_id,)).fetchone()[0]

            completed = conn.execute("""
                SELECT COUNT(*)
                FROM Tasks
                WHERE user_id = ? AND status = 'Completed'
            """, (user_id,)).fetchone()[0]

            pending = conn.execute("""
                SELECT COUNT(*)
                FROM Tasks
                WHERE user_id = ? AND status = 'Pending'
            """, (user_id,)).fetchone()[0]

            in_progress = conn.execute("""
                SELECT COUNT(*)
                FROM Tasks
                WHERE user_id = ? AND status = 'In Progress'
            """, (user_id,)).fetchone()[0]

            print(f"\nUser: {name}")
            print(f"  Total Tasks       : {total}")
            print(f"  Completed        : {completed}")
            print(f"  Pending          : {pending}")
            print(f"  In Progress      : {in_progress}")

    print("\n===================================")


def view_all_tasks():
    print("\n========== ALL TASKS ==========")

    with sqlite3.connect(DB_NAME) as conn:
        tasks = conn.execute("""
            SELECT Users.name, Tasks.task_id, Tasks.title,
                   Tasks.deadline, Tasks.priority, Tasks.status
            FROM Tasks
            JOIN Users ON Tasks.user_id = Users.user_id
            ORDER BY Tasks.task_id
        """).fetchall()

    if not tasks:
        print("No tasks found.")
    else:
        for name, task_id, title, deadline, priority, status in tasks:
            print(f"\nUser: {name}")
            print(f"Task ID  : {task_id}")
            print(f"Title    : {title}")
            print(f"Deadline : {deadline if deadline else 'Not set'}")
            print(f"Priority : {priority}")
            print(f"Status   : {status}")
            print("--------------------------------")

    print("===============================")


def admin_menu():
    while True:
        print("\n========== ADMIN MENU ==========")
        print("1. View Dashboard")
        print("2. View User Progress")
        print("3. view All Tasks")
        print("4. Logout")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            admin_dashboard()

        elif choice == "2":
            view_user_progress()

        elif choice == "3":
            view_all_tasks()

        elif choice == "4":
            print("\nAdmin logged out.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    if admin_login():
        admin_menu()