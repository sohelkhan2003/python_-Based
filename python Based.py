# Initialize an empty to-do list as a list of dictionaries
todo_list = []

# Function to add a task to the to-do list
def add_task(description, due_date, priority):
    task = {
        "Description": description,
        "Due Date": due_date,
        "Priority": priority,
        "Completed": False  # Initially, the task is not completed
    }
    todo_list.append(task)
    print("Task added successfully!")

# Function to display the to-do list
def display_todo_list():
    if not todo_list:
        print("To-Do list is empty.")
    else:
        print("\nTo-Do List:")
        for index, task in enumerate(todo_list):
            status = "Completed" if task["Completed"] else "Incomplete"
            print(f"{index + 1}. Description: {task['Description']}, Due Date: {task['Due Date']}, Priority: {task['Priority']}, Status: {status}")

# Function to mark a task as completed
def complete_task(task_index):
    if 0 <= task_index < len(todo_list):
        todo_list[task_index]["Completed"] = True
        print("Task marked as completed.")
    else:
        print("Invalid task index.")

# Function to update a task
def update_task(task_index, description, due_date, priority):
    if 0 <= task_index < len(todo_list):
        todo_list[task_index]["Description"] = description
        todo_list[task_index]["Due Date"] = due_date
        todo_list[task_index]["Priority"] = priority
        print("Task updated successfully.")
    else:
        print("Invalid task index.")

# Function to remove a task
def remove_task(task_index):
    if 0 <= task_index < len(todo_list):
        removed_task = todo_list.pop(task_index)
        print(f"Task removed: {removed_task['Description']}")
    else:
        print("Invalid task index.")

# Example usage:
while True:
    print("\nOptions:")
    print("1. Add Task")
    print("2. Display To-Do List")
    print("3. Mark Task as Completed")
    print("4. Update Task")
    print("5. Remove Task")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        description = input("Enter task description: ")
        due_date = input("Enter due date (YYYY-MM-DD): ")
        priority = input("Enter priority (High/Medium/Low): ")
        add_task(description, due_date, priority)

    elif choice == "2":
        display_todo_list()

    elif choice == "3":
        task_index = int(input("Enter the index of the task to mark as completed: ")) - 1
        complete_task(task_index)

    elif choice == "4":
        task_index = int(input("Enter the index of the task to update: ")) - 1
        description = input("Enter updated task description: ")
        due_date = input("Enter updated due date (YYYY-MM-DD): ")
        priority = input("Enter updated priority (High/Medium/Low): ")
        update_task(task_index, description, due_date, priority)

    elif choice == "5":
        task_index = int(input("Enter the index of the task to remove: ")) - 1
        remove_task(task_index)

    elif choice == "6":
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")