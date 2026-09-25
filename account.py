# account.py – Simple account management for Galactic Defenders prototype

"""Account module providing registration, login, and persistence.

Data is stored in a JSON file ``users.json`` located in ``settings.BASE_DIR``.
The structure is::

    {
        "users": {
            "alice": {
                "password": "secret",
                "admin": true,
                "player_data": { ... }
            },
            ...
        }
    }

Passwords are stored in plain text for this prototype (acceptable per user consent).
"""

import json
import os
from typing import Dict, Any

# Import the BASE_DIR from settings so the file lives alongside other data files.
try:
    from settings import BASE_DIR
except Exception:
    # Fallback: use the directory of this file if settings cannot be imported (e.g., tests).
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_USERS_FILE = os.path.join(BASE_DIR, "users.json")


def _load_all_users() -> Dict[str, Any]:
    """Load the entire users JSON structure.

    Returns an empty dict if the file does not exist.
    """
    if not os.path.exists(_USERS_FILE):
        return {"users": {}}
    with open(_USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file – start fresh to avoid crashes.
            return {"users": {}}


def _save_all_users(data: Dict[str, Any]) -> None:
    """Write the full users JSON structure back to disk.

    The directory is created if missing.
    """
    os.makedirs(os.path.dirname(_USERS_FILE), exist_ok=True)
    with open(_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def register(username: str, password: str, admin: bool = False) -> bool:
    """Create a new user.

    Returns ``True`` on success, ``False`` if the username already exists.
    """
    if not username or not password:
        return False
    data = _load_all_users()
    users = data.setdefault("users", {})
    if username in users:
        return False
    # Determine if this is the first user ever created.
    is_first_user = len(users) == 0
    # The first user is forced to be admin. Subsequent users cannot become admin.
    users[username] = {
        "password": password,
        "admin": is_first_user,
        "player_data": {}
    }
    # Record the primary admin username for easy lookup.
    if is_first_user:
        data["primary_admin"] = username
    data["last_logged_in"] = username
    _save_all_users(data)
    return True


def login(username: str, password: str) -> bool:
    """Validate credentials and persist session.

    Returns ``True`` if the username exists and the password matches.
    """
    data = _load_all_users()
    users = data.get("users", {})
    user = users.get(username)
    if not user:
        return False
    if user.get("password") == password:
        data["last_logged_in"] = username
        _save_all_users(data)
        return True
    return False


def set_active_session(username: str | None) -> None:
    """Persist the currently logged-in user session."""
    data = _load_all_users()
    data["last_logged_in"] = username
    _save_all_users(data)


def get_active_session() -> str | None:
    """Retrieve the last logged-in username if valid."""
    data = _load_all_users()
    last_user = data.get("last_logged_in")
    users = data.get("users", {})
    if last_user and last_user in users:
        return last_user
    return None


def load_user_data(username: str) -> Dict[str, Any]:
    """Fetch the stored ``player_data`` for *username*.

    If the user does not exist an empty dict is returned.
    """
    data = _load_all_users()
    users = data.get("users", {})
    user = users.get(username, {})
    return user.get("player_data", {})


def save_user_data(username: str, player_data: Dict[str, Any]) -> None:
    """Persist *player_data* for *username*.

    The function creates the user entry if it does not already exist.
    """
    data = _load_all_users()
    users = data.setdefault("users", {})
    if username not in users:
        # Initialise a non‑admin account if missing.
        users[username] = {"password": "", "admin": False, "player_data": {}}
    users[username]["player_data"] = player_data
    _save_all_users(data)


def is_admin(username: str) -> bool:
    """Return ``True`` if *username* is flagged as an admin.
    """
    data = _load_all_users()
    users = data.get("users", {})
    return bool(users.get(username, {}).get("admin"))


def list_all_usernames() -> list:
    """Return a list of all registered usernames.
    """
    data = _load_all_users()
    return list(data.get("users", {}).keys())

def is_primary_admin(username: str) -> bool:
    """Return True if *username* is the primary admin (first created account)."""
    data = _load_all_users()
    return data.get("primary_admin") == username


def delete_user(username: str) -> bool:
    """Remove *username* from the users database.

    Returns True on success, False if the user does not exist or is the primary admin.
    """
    data = _load_all_users()
    users = data.get("users", {})
    if username not in users:
        return False
    # Prevent deleting the primary admin account.
    if data.get("primary_admin") == username:
        return False
    del users[username]
    if data.get("last_logged_in") == username:
        data["last_logged_in"] = None
    _save_all_users(data)
    return True

# Added set_admin function to modify admin flag

def set_admin(username: str, admin: bool) -> bool:
    """Set the admin flag for a user.

    Returns True on success, False if the user does not exist or is the primary admin.
    """
    data = _load_all_users()
    users = data.get("users", {})
    if username not in users:
        return False
    # Prevent changing the primary admin's admin status.
    if data.get("primary_admin") == username:
        return False
    users[username]["admin"] = admin
    _save_all_users(data)
    return True



# End of account.py
