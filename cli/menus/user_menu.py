# cli/menus/user_menu.py
from cli.client import client
from cli.display import (
    display_menu, display_user_table, display_user_details,
    display_user_summary, get_input, print_success, print_error, print_header
)

def user_menu():
    """User management menu"""
    while True:
        choice = display_menu(
            "User Management",
            [
                "Create User",
                "List All Users",
                "Get User Details",
                "Get User Summary",
                "Update User",
                "Delete User"
            ]
        )
        
        if choice == "0":
            break
        elif choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            get_user_details()
        elif choice == "4":
            get_user_summary()
        elif choice == "5":
            update_user()
        elif choice == "6":
            delete_user()
        else:
            print_error("Invalid option. Please try again.")

def create_user():
    """Create a new user"""
    print_header("Create New User")
    name = get_input("Enter name")
    email = get_input("Enter email")
    
    user = client.create_user(name, email)
    if user:
        print_success(f"User created successfully! ID: {user['id']}")

def list_users():
    """List all users"""
    print_header("All Users")
    response = client.get_users()
    print(type(response))
    if response:
        users = response.get("users", [])
        display_user_table(users)

def get_user_details():
    """Get user details by selection"""
    print_header("Get User Details")
    
    # First, show all users
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    # Let user select
    try:
        choice = int(get_input("\nEnter S.No to view details"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            user = client.get_user(user_id)
            if user:
                display_user_details(user)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Please enter a valid number.")

def get_user_summary():
    """Get user summary by selection"""
    print_header("Get User Summary")
    
    # Show all users
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    # Let user select
    try:
        choice = int(get_input("\nEnter S.No to view summary"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            summary = client.get_user_summary(user_id)
            if summary:
                display_user_summary(summary)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Please enter a valid number.")

def update_user():
    """Update user"""
    print_header("Update User")
    
    # Show all users
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    try:
        choice = int(get_input("\nEnter S.No to update"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            
            # Get update data
            name = get_input("New name (press Enter to skip)", required=False)
            email = get_input("New email (press Enter to skip)", required=False)
            is_active = get_input("Active status (yes/no, press Enter to skip)", required=False)
            
            update_data = {}
            if name:
                update_data["name"] = name
            if email:
                update_data["email"] = email
            if is_active:
                update_data["is_active"] = is_active.lower() in ["yes", "y", "true"]
            
            if update_data:
                user = client.update_user(user_id, **update_data)
                if user:
                    print_success("User updated successfully!")
            else:
                print_error("No fields to update.")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Please enter a valid number.")

def delete_user():
    """Delete user"""
    print_header("Delete User")
    
    # Show all users
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    try:
        choice = int(get_input("\nEnter S.No to delete"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            confirm = get_input(f"Are you sure you want to delete user {users[choice-1]['name']}? (yes/no)")
            
            if confirm.lower() in ["yes", "y"]:
                if client.delete_user(user_id):
                    print_success("User deleted successfully!")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Please enter a valid number.")