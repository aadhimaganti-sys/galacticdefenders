# admin_panel.py – Console admin interface (only for primary admin)

"""Admin panel for Galactic Defenders.

The panel is reachable only when the logged‑in user is the primary admin
(the very first account created). It provides simple console commands to
manage accounts and tweak game settings. Non‑admin users cannot invoke the
panel because `main.py` checks `account.is_admin(state.current_user)` before
calling `run_admin_menu()`.

Features:
* List all registered usernames.
* View a user's stored ``player_data``.
* Edit a user's high score (stored in ``player_data['credits']`` for demo).
* Delete a user (cannot delete the primary admin).
* Exit back to the game.

All changes are persisted via ``account.save_user_data`` or ``account.delete_user``.
"""

import sys
from typing import Any

import account
import state


def _prompt(msg: str) -> str:
    """Utility to get input and strip whitespace."""
    return input(msg).strip()


def _print_header(title: str) -> None:
    print("\n" + "=" * 40)
    print(f"{title}")
    print("=" * 40)


def _list_users() -> None:
    _print_header("Registered Users")
    for username in account.list_all_usernames():
        admin_flag = " (admin)" if account.is_admin(username) else ""
        primary = " [primary]" if getattr(account, "is_primary_admin", lambda u: False)(username) else ""
        print(f"- {username}{admin_flag}{primary}")


def _view_user_data() -> None:
    username = _prompt("Enter username to view data: ")
    data = account.load_user_data(username)
    if not data:
        print(f"No data found for user '{username}'.")
        return
    print(f"Data for {username}: {data}")


def _edit_user_score() -> None:
    username = _prompt("Enter username to edit score: ")
    data = account.load_user_data(username)
    if not data:
        print(f"User '{username}' not found.")
        return
    current = data.get("credits", 0)
    print(f"Current credits for {username}: {current}")
    try:
        new_val = int(_prompt("Enter new credits value: "))
    except ValueError:
        print("Invalid integer – aborting edit.")
        return
    data["credits"] = new_val
    account.save_user_data(username, data)
    print(f"Credits for {username} updated to {new_val}.")


def _delete_user() -> None:
    username = _prompt("Enter username to delete: ")
    # Protect the primary admin from deletion.
    if getattr(account, "is_primary_admin", lambda u: False)(username):
        print("Cannot delete the primary admin account.")
        return
    if account.delete_user(username):
        print(f"User '{username}' deleted.")
        if state.current_user == username:
            state.current_user = None
    else:
        print(f"User '{username}' does not exist.")


def run_admin_menu() -> None:
    """Main loop for the admin console.

    Called from ``main.py`` when the logged‑in user is an admin (checked
    beforehand). The menu runs until the admin chooses to exit.
    """
    if not state.current_user or not account.is_admin(state.current_user):
        print("Admin panel access denied – not logged in as admin.")
        return

    while True:
        _print_header(f"Admin Panel – Logged in as {state.current_user}")
        print("Select an option:")
        print("1) List all users")
        print("2) View user data")
        print("3) Edit user credits (demo setting)")
        print("4) Delete user")
        print("5) Exit admin panel")
        choice = _prompt("Enter number: ")
        if choice == "1":
            _list_users()
        elif choice == "2":
            _view_user_data()
        elif choice == "3":
            _edit_user_score()
        elif choice == "4":
            _delete_user()
        elif choice == "5":
            print("Leaving admin panel.")
            break
        else:
            print("Invalid choice – try again.")
        input("Press Enter to continue...")

# End of admin_panel.py
