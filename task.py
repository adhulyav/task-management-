
from datetime import datetime
from user_auth import connect_db


# CHECK DEADLINE FORMAT
def valid_deadline(deadline):
    if not deadline:
        return True

    try:
        datetime.strptime(deadline, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# 1. ADD TASK
def add_task(user):
    print("\n--- Add New Task ---")

    title = input("Enter task title: ").strip()
    deadline = input(
        "Enter deadline (YYYY-MM-DD, or press Enter to skip): "
    ).strip()

    if not title:
        print("Task title is required.")
        return

    if not valid_deadline(deadline):
        print("Invalid deadline. Use YYYY-MM-DD.")
        return

    print("\nPriority: 1. Low  2. Medium  3. High")
    choice = input("Choose priority: ").strip()

    priorities = {"1": "Low", "2": "Medium", "3": "High"}

    if choice not in priorities:
        print("Invalid priority.")
        return

    with connect_db() as conn:
        conn.execute("""
            INSERT INTO Tasks (user_id, title, deadline, priority)
            VALUES (?, ?, ?, ?)
        """, (
            user["user_id"],
            title,
            deadline or None,
            priorities[choice]
        ))

    print("Task added successfully!")


# 2. VIEW TASKS
def view_tasks(user):
    with connect_db() as conn:
        tasks = conn.execute("""
            SELECT task_id, title, deadline, priority, status
            FROM Tasks
            WHERE user_id = ?
            ORDER BY task_id DESC
        """, (user["user_id"],)).fetchall()

    print("\n--- My Tasks ---")

    if not tasks:
        print("No tasks found.")
        return False

    for task in tasks:
        print(f"\nID: {task[0]}")
        print(f"Title: {task[1]}")
        print(f"Deadline: {task[2] or 'Not set'}")
        print(f"Priority: {task[3]}")
        print(f"Status: {task[4]}")

    return True


# 3. UPDATE TASK STATUS
def update_task_status(user):
    if not view_tasks(user):
        return

    task_id = input("\nEnter task ID to update: ").strip()

    if not task_id.isdigit():
        print("Enter a valid task ID.")
        return

    print("1. Pending")
    print("2. In Progress")
    print("3. Completed")

    choice = input("Choose new status: ").strip()

    statuses = {
        "1": "Pending",
        "2": "In Progress",
        "3": "Completed"
    }

    if choice not in statuses:
        print("Invalid status.")
        return

    with connect_db() as conn:
        cursor = conn.execute("""
            UPDATE Tasks
            SET status = ?
            WHERE task_id = ? AND user_id = ?
        """, (
            statuses[choice],
            int(task_id),
            user["user_id"]
        ))

    if cursor.rowcount:
        print("Task status updated!")
    else:
        print("Task not found.")


# 4. EDIT TASK
def edit_task(user):
    if not view_tasks(user):
        return

    task_id = input("\nEnter task ID to edit: ").strip()

    if not task_id.isdigit():
        print("Enter a valid task ID.")
        return

    with connect_db() as conn:
        task = conn.execute("""
            SELECT title, deadline
            FROM Tasks
            WHERE task_id = ? AND user_id = ?
        """, (int(task_id), user["user_id"])).fetchone()

        if not task:
            print("Task not found.")
            return

        title = input(
            f"New title [{task[0]}]: "
        ).strip() or task[0]

        deadline = input(
            f"New deadline [{task[1] or 'Not set'}] "
            "(YYYY-MM-DD, Enter to keep, - to clear): "
        ).strip()

        if deadline == "-":
            deadline = None
        elif deadline == "":
            deadline = task[1]

        if not valid_deadline(deadline):
            print("Invalid deadline. Use YYYY-MM-DD.")
            return

        conn.execute("""
            UPDATE Tasks
            SET title = ?, deadline = ?
            WHERE task_id = ? AND user_id = ?
        """, (
            title,
            deadline,
            int(task_id),
            user["user_id"]
        ))

    print("Task updated successfully!")


# 5. DELETE TASK
def delete_task(user):
    if not view_tasks(user):
        return

    task_id = input("\nEnter task ID to delete: ").strip()

    if not task_id.isdigit():
        print("Enter a valid task ID.")
        return

    confirm = input(
        "Are you sure you want to delete this task? (y/n): "
    ).strip().lower()

    if confirm != "y":
        print("Deletion cancelled.")
        return

    with connect_db() as conn:
        cursor = conn.execute("""
            DELETE FROM Tasks
            WHERE task_id = ? AND user_id = ?
        """, (int(task_id), user["user_id"]))

    if cursor.rowcount:
        print("Task deleted successfully!")
    else:
        print("Task not found.")


# 6. TASK MENU
def task_menu(user):
    while True:
        print("\n--- Task Management Menu ---")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task Status")
        print("4. Edit Task")
        print("5. Delete Task")
        print("6. Logout")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_task(user)
        elif choice == "2":
            view_tasks(user)
        elif choice == "3":
            update_task_status(user)
        elif choice == "4":
            edit_task(user)
        elif choice == "5":
            delete_task(user)
        elif choice == "6":
            print("Logged out successfully.")
            break
        else:
            print("Invalid choice. Try again.")