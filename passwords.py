import sqlite3
import hashlib
import os
import json
import pwinput
import secrets
import string
import socket
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet

# -----------------------------
# Color codes for terminal output
# -----------------------------
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
RESET = "\033[0m"

DB_FILE = "database.db"

# -----------------------------
# Firebase Initialization
# -----------------------------
db_online = None  # This will hold our Firestore client

def init_firebase():
    """
    Initialize Firebase using your private serviceAccountKey.json file.
    If initialization fails, db_online remains None.
    """
    global db_online
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db_online = firestore.client()
        print(GREEN + "Firebase initialized successfully." + RESET)
    except Exception as e:
        print(RED + "Error initializing Firebase: " + str(e) + RESET)
        db_online = None

def internet_available(host="8.8.8.8", port=53, timeout=3):
    """
    Check if there is an internet connection by trying to connect to a known host.
    Default is Google's public DNS.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def backup_online_data(db_manager):
    """
    Extracts the entire local database (both users and passwords) and uploads it to Firestore.
    The backup is stored under collection 'db_backup' in document 'backup'.
    """
    if db_online is None:
        print(RED + "Firebase not initialized. Cannot backup online." + RESET)
        return

    if not internet_available():
        print(RED + "No internet connection. Online backup skipped." + RESET)
        return

    try:
        cur = db_manager.conn.cursor()
        # Fetch users as dictionaries
        cur.execute("SELECT username, password, security_question, security_answer FROM users")
        users_columns = [desc[0] for desc in cur.description]
        users_data = [dict(zip(users_columns, row)) for row in cur.fetchall()]

        # Fetch passwords as dictionaries
        cur.execute("SELECT id, username, platform, platform_username, email, password FROM passwords")
        pass_columns = [desc[0] for desc in cur.description]
        passwords_data = [dict(zip(pass_columns, row)) for row in cur.fetchall()]

        backup_dict = {"users": users_data, "passwords": passwords_data}

        db_online.collection("db_backup").document("backup").set(backup_dict)
        print(GREEN + "Online backup successful!" + RESET)
    except Exception as e:
        print(RED + "Error during online backup: " + str(e) + RESET)

def restore_online_data(db_manager):
    """
    Restores the entire database (users and passwords) from the online backup.
    WARNING: This will delete your current local data and replace it with the backup.
    """
    if db_online is None:
        print(RED + "Firebase not initialized. Cannot restore online backup." + RESET)
        return

    if not internet_available():
        print(RED + "No internet connection. Cannot restore online backup." + RESET)
        return

    try:
        doc = db_online.collection("db_backup").document("backup").get()
        if doc.exists:
            data = doc.to_dict()
            cur = db_manager.conn.cursor()
            # Delete current data
            cur.execute("DELETE FROM users")
            cur.execute("DELETE FROM passwords")
            # Restore users
            for user in data.get("users", []):
                cur.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                            (user["username"], user["password"], user["security_question"], user["security_answer"]))
            # Restore passwords
            for entry in data.get("passwords", []):
                cur.execute("INSERT INTO passwords (id, username, platform, platform_username, email, password) VALUES (?, ?, ?, ?, ?, ?)",
                            (entry["id"], entry["username"], entry["platform"], entry["platform_username"], entry["email"], entry["password"]))
            db_manager.conn.commit()
            print(GREEN + "Online restore successful!" + RESET)
        else:
            print(RED + "No online backup found." + RESET)
    except Exception as e:
        print(RED + "Error during online restore: " + str(e) + RESET)

# -----------------------------
# Encryption Utilities
# -----------------------------
def load_key():
    """
    Loads the secret key from 'secret.key'.
    If the file does not exist, it generates a new key and saves it.
    """
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

KEY = load_key()
cipher_suite = Fernet(KEY)

def encrypt_data(data):
    """Encrypts a string and returns a decoded ciphertext."""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(data):
    """Decrypts the ciphertext and returns the original string."""
    return cipher_suite.decrypt(data.encode()).decode()

# -----------------------------
# Password Strength & Generation
# -----------------------------
def check_password_strength(password: str) -> str:
    """
    Checks the strength of the password.
    Criteria:
      - Length at least 8
      - Contains lowercase letters
      - Contains uppercase letters
      - Contains digits
      - Contains special characters
    Returns: A string rating: Weak, Medium, Strong, or Very Strong.
    """
    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score == 3:
        return "Medium"
    elif score == 4:
        return "Strong"
    else:
        return "Very Strong"

def auto_generate_password(length=12) -> str:
    """
    Generates a random password of specified length ensuring at least one lowercase, one uppercase,
    one digit, and one special character.
    """
    if length < 8:
        length = 8
    lower = secrets.choice(string.ascii_lowercase)
    upper = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~")
    if length > 4:
        rest = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~") for _ in range(length - 4))
    else:
        rest = ''
    password_list = list(lower + upper + digit + special + rest)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)

# -----------------------------
# Database & User Management
# -----------------------------
class DatabaseManager:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                security_question TEXT NOT NULL,
                security_answer TEXT NOT NULL
            )
        ''')
        # Create passwords table
        c.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                platform TEXT NOT NULL,
                platform_username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def close(self):
        self.conn.close()

class UserManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def encrypt_password(self, password):
        # For login passwords, we use a one-way SHA256 hash.
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("signup")
        username = input(GREEN + "📝  Enter username (or type 'back' to go back to main menu): " + RESET)
        if username.lower() == "back":
            return
        elif not username.isalnum():
            input(RED + "❌ Please enter a valid username." + RESET)
            self.signup()
            return
        # Check if the username already exists
        cur = self.db.conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            input(RED + "❌ Username already exists! Try another." + RESET)
            self.signup()
            return
        password = UserManager.get_password(GREEN + "🔒  Enter password (or type 'auto' to generate one, 'back' to return): " + RESET)
        if password.lower() == "back":
            return
        if password.lower() == "auto":
            password = auto_generate_password()
            print(YELLOW + f"Auto-generated Password: {password}" + RESET)
        rating = check_password_strength(password)
        print(YELLOW + f"Password Strength: {rating}" + RESET)
        if rating == "Weak":
            choice = input(RED + "Your password is weak. Do you want to re-enter? (yes/no): " + RESET)
            if choice.lower() in ["yes", "y"]:
                self.signup()
                return
        if not password:
            input(RED + "❌ Please enter a valid password." + RESET)
            self.signup()
            return
        confirm = input(YELLOW + f"\nYour password is: {GREEN}{password}{YELLOW}. Do you confirm this password? (yes/no): " + RESET)
        if confirm.lower() in ["yes", "y"]:
            security_question = input(YELLOW + "🔐 Set a security question (e.g., Your pet's name, or type 'back' to return): " + RESET)
            if security_question.lower() == "back":
                return
            security_answer = input(YELLOW + "🔑 Answer (or type 'back' to return): " + RESET).lower()
            if security_answer.lower() == "back":
                return
            hashed_password = self.encrypt_password(password)
            # Encrypt security question and answer
            encrypted_question = encrypt_data(security_question)
            encrypted_answer = encrypt_data(security_answer)
            cur.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                        (username, hashed_password, encrypted_question, encrypted_answer))
            self.db.conn.commit()
            print("\n" + GREEN + "✅ Signup successful!" + RESET)
        elif confirm.lower() in ["no", "n"]:
            input(RED + "❌ Please enter password again! Press enter to continue." + RESET)
            self.signup()
        else:
            input(RED + "❌ Invalid Input!" + RESET)
            self.signup()

    @staticmethod
    def get_password(txt):
        return pwinput.pwinput(prompt=txt)

    def list_users(self):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("listusers")
        cur = self.db.conn.cursor()
        cur.execute("SELECT username FROM users")
        users = cur.fetchall()
        if users:
            print(CYAN, end="")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user[0]}")
            print(RESET)
        else:
            print(RED + "❌ No users found!" + RESET)
        input()

    def login(self):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("login")
        print("[NOTE]: Press F for forgotten password or type 'back' to go back to main menu.")
        username = input(BLUE + "👤 Enter username (or 'back' to return): " + RESET)
        if username.lower() == "f":
            self.forget_password()
            return None
        if username.lower() == "back":
            return None
        password = self.get_password(BLUE + "🔑 Enter password (or type 'back' to return): " + RESET)
        if password.lower() == "back":
            return None
        cur = self.db.conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row is None:
            input(RED + "\n❌ Invalid username or password!" + RESET)
            return None
        stored_hash = row[0]
        if stored_hash == self.encrypt_password(password):
            print("\n" + GREEN + "✅ Login successful! Welcome back!" + RESET)
            return username
        else:
            input("\n" + RED + "❌ Invalid username or password!" + RESET)
            return None

    def forget_password(self):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("forgetpass")
        username = input(YELLOW + "👤 Enter your username (or type 'back' to return): " + RESET)
        if username.lower() == "back":
            return
        cur = self.db.conn.cursor()
        cur.execute("SELECT security_question, security_answer FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            # Decrypt the stored security question for display
            decrypted_question = decrypt_data(row[0])
            print(YELLOW + "Q: " + decrypted_question + RESET)
            answer = input(YELLOW + "🔑 Answer (or type 'back' to return): " + RESET).lower()
            if answer.lower() == "back":
                return
            decrypted_answer = decrypt_data(row[1])
            if answer == decrypted_answer:
                new_password = UserManager.get_password(GREEN + "🔒 Enter new password (or type 'auto' to generate, 'back' to return): " + RESET)
                if new_password.lower() == "back":
                    return
                if new_password.lower() == "auto":
                    new_password = auto_generate_password()
                    print(YELLOW + f"Auto-generated Password: {new_password}" + RESET)
                rating = check_password_strength(new_password)
                print(YELLOW + f"New Password Strength: {rating}" + RESET)
                if rating == "Weak":
                    choice = input(RED + "Your new password is weak. Do you want to re-enter? (yes/no): " + RESET)
                    if choice.lower() in ["yes", "y"]:
                        self.forget_password()
                        return
                hashed_password = self.encrypt_password(new_password)
                cur.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
                self.db.conn.commit()
                input(GREEN + "✅ Password reset successful!" + RESET)
            else:
                input(RED + "❌ Incorrect answer!" + RESET)
        else:
            input(RED + "❌ Username not found!" + RESET)
        self.login()

    def delete_account(self):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("delacc")
        username = input(YELLOW + "🗑️  Enter username (or type 'back' to return): " + RESET)
        if username.lower() == "back":
            return
        password = self.get_password(YELLOW + "🔑  Enter password (or type 'back' to return): " + RESET)
        if password.lower() == "back":
            return
        cur = self.db.conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row and row[0] == self.encrypt_password(password):
            confirm = input(YELLOW + "\nAll your saved passwords will be removed. Are you sure you want to continue? (yes/no): " + RESET)
            if confirm.lower() in ["yes", "y"]:
                cur.execute("DELETE FROM users WHERE username = ?", (username,))
                self.db.conn.commit()
                print(GREEN + "✅ Account deleted!" + RESET)
            elif confirm.lower() in ["no", "n"]:
                input(RED + "❌ Deletion of Account canceled." + RESET)
                self.signup()
            else:
                input(RED + "❌ Invalid Input!" + RESET)
                self.signup()
        else:
            print(RED + "❌ Invalid username or password!" + RESET)

class PasswordManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_password(self, username):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("addpass")
        platform = input(GREEN + "🌐 Enter platform name (or type 'back' to return): " + RESET).lower()
        if platform.lower() == "back":
            return
        platform_username = input(GREEN + "👤 Enter username (or type 'back' to return): " + RESET)
        if platform_username.lower() == "back":
            return
        email = input(GREEN + "📧 Enter email (or type 'back' to return): " + RESET)
        if email.lower() == "back":
            return
        password = UserManager.get_password(GREEN + "🔒 Enter password (or type 'auto' to generate, 'back' to return): " + RESET)
        if password.lower() == "back":
            return
        if password.lower() == "auto":
            password = auto_generate_password()
            print(YELLOW + f"Auto-generated Password: {password}" + RESET)
        rating = check_password_strength(password)
        print(YELLOW + f"Password Strength: {rating}" + RESET)
        if rating == "Weak":
            choice = input(RED + "Your password is weak. Do you want to re-enter? (yes/no): " + RESET)
            if choice.lower() in ["yes", "y"]:
                self.add_password(username)
                return
        confirm = input(YELLOW + f"\nYour password is: {GREEN}{password}{YELLOW}. Do you confirm this password? (yes/no): " + RESET)
        if confirm.lower() in ["yes", "y"]:
            # Encrypt the platform password before storing it
            encrypted_pass = encrypt_data(password)
            cur = self.db.conn.cursor()
            cur.execute("INSERT INTO passwords (username, platform, platform_username, email, password) VALUES (?, ?, ?, ?, ?)",
                        (username, platform, platform_username, email, encrypted_pass))
            self.db.conn.commit()
            print(GREEN + "✅ Password saved!" + RESET)
        elif confirm.lower() in ["no", "n"]:
            input(RED + "❌ Please enter password again! Press enter to continue." + RESET)
            self.add_password(username)
        else:
            input(RED + "❌ Invalid Input!" + RESET)
            self.add_password(username)

    def access_passwords(self, username):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("accesspass")
        platform = input(CYAN + "🔎 Enter platform name (or type 'back' to return): " + RESET).lower()
        if platform.lower() == "back":
            return
        cur = self.db.conn.cursor()
        cur.execute("SELECT platform_username, email, password FROM passwords WHERE username = ? AND platform = ?", (username, platform))
        row = cur.fetchone()
        if row:
            decrypted_pass = decrypt_data(row[2])
            print(CYAN + f"Platform: {platform}\nUsername: {row[0]}\nEmail: {row[1]}\nPassword: {decrypted_pass}" + RESET)
        else:
            print(RED + "❌ No saved credentials for this platform!" + RESET)
        input("\nPress Enter to continue...")

    def delete_password(self, username):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("delpass")
        platform = input(YELLOW + "🗑️ Enter platform name to delete (or type 'back' to return): " + RESET).lower()
        if platform.lower() == "back":
            return
        cur = self.db.conn.cursor()
        cur.execute("SELECT id FROM passwords WHERE username = ? AND platform = ?", (username, platform))
        row = cur.fetchone()
        if row:
            cur.execute("DELETE FROM passwords WHERE id = ?", (row[0],))
            self.db.conn.commit()
            print(GREEN + "✅ Password deleted!" + RESET)
        else:
            print(RED + "❌ No such password found!" + RESET)
        input()

    def edit_password(self, username):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("editpass")
        platform = input(YELLOW + "✏️ Enter platform name to edit (or type 'back' to return): " + RESET).lower()
        if platform.lower() == "back":
            return
        cur = self.db.conn.cursor()
        cur.execute("SELECT id FROM passwords WHERE username = ? AND platform = ?", (username, platform))
        row = cur.fetchone()
        if row:
            platform_username = input(YELLOW + "👤 Enter new username (or type 'back' to return): " + RESET)
            if platform_username.lower() == "back":
                return
            new_password = input(YELLOW + "🔒 Enter new password (or type 'auto' to generate, 'back' to return): " + RESET)
            if new_password.lower() == "back":
                return
            if new_password.lower() == "auto":
                new_password = auto_generate_password()
                print(YELLOW + f"Auto-generated Password: {new_password}" + RESET)
            rating = check_password_strength(new_password)
            print(YELLOW + f"New Password Strength: {rating}" + RESET)
            if rating == "Weak":
                choice = input(RED + "Your new password is weak. Do you want to re-enter? (yes/no): " + RESET)
                if choice.lower() in ["yes", "y"]:
                    self.edit_password(username)
                    return
            encrypted_pass = encrypt_data(new_password)
            cur.execute("UPDATE passwords SET platform_username = ?, password = ? WHERE id = ?", (platform_username, encrypted_pass, row[0]))
            self.db.conn.commit()
            print(GREEN + "✅ Password updated successfully!" + RESET)
        else:
            print(RED + "❌ No saved credentials for this platform!" + RESET)
        input("\nPress Enter to continue...")

    def show_listed_platforms(self, username):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("showplat")
        cur = self.db.conn.cursor()
        cur.execute("SELECT DISTINCT platform FROM passwords WHERE username = ?", (username,))
        rows = cur.fetchall()
        if rows:
            for i, row in enumerate(rows, 1):
                print(CYAN + f"{i}. {row[0].title()}" + RESET)
        else:
            print(RED + "❌ No saved platforms found!" + RESET)
        input()

    def check_password_health(self, username):
        os.system("cls" if os.name == "nt" else "clear")
        UI.print_heading("passhealth")
        cur = self.db.conn.cursor()
        cur.execute("SELECT platform, password FROM passwords WHERE username = ?", (username,))
        rows = cur.fetchall()
        if rows:
            for row in rows:
                platform, encrypted_pass = row
                plain_password = decrypt_data(encrypted_pass)
                rating = check_password_strength(plain_password)
                print(CYAN + f"Platform: {platform.title()} -> Password Strength: {rating}" + RESET)
        else:
            print(RED + "❌ No saved platform passwords found!" + RESET)
        input("\nPress Enter to continue...")

class UI:
    @staticmethod
    def print_heading(txt):
        if txt == "main":
            print(GREEN + "=" * 40)
            print("⭐ Welcome to Secure Login System ⭐".center(40))
            print("=" * 40 + RESET)
        elif txt == "signup":
            print(GREEN + "=" * 25)
            print("⭐ Signup Form ⭐".center(25))
            print("=" * 25 + RESET)
        elif txt == "login":
            print(GREEN + "=" * 55)
            print("⭐ Login Form ⭐".center(55))
            print("=" * 55 + RESET)
        elif txt == "passmenu":
            print(GREEN + "=" * 35)
            print("⭐ Password Manager ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "showplat":
            print(GREEN + "=" * 45)
            print("⭐ List of Platforms Saved ⭐".center(45))
            print("=" * 45 + RESET)
        elif txt == "delacc":
            print(GREEN + "=" * 45)
            print("⭐ Delete Account ⭐".center(45))
            print("=" * 45 + RESET)
        elif txt == "editpass":
            print(GREEN + "=" * 35)
            print("⭐ Edit Password ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "delpass":
            print(GREEN + "=" * 35)
            print("⭐ Delete Password ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "accesspass":
            print(GREEN + "=" * 35)
            print("⭐ Access Password ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "addpass":
            print(GREEN + "=" * 35)
            print("⭐ Add Password ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "listusers":
            print(GREEN + "=" * 35)
            print("⭐ List of Users ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "forgetpass":
            print(GREEN + "=" * 35)
            print("⭐ Forget Password ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "passhealth":
            print(GREEN + "=" * 35)
            print("⭐ Password Health Check ⭐".center(35))
            print("=" * 35 + RESET)
        elif txt == "backupmenu":
            print(GREEN + "=" * 40)
            print("⭐ Backup & Restore Menu ⭐".center(40))
            print("=" * 40 + RESET)

class Application:
    def __init__(self, db_file):
        self.db_manager = DatabaseManager(db_file)
        self.user_manager = UserManager(self.db_manager)
        self.password_manager = PasswordManager(self.db_manager)

    def backup_restore_menu(self):
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            UI.print_heading("backupmenu")
            print(CYAN + "1.  Online Backup" + RESET)
            print(CYAN + "2.  Online Restore" + RESET)
            print(CYAN + "3.  Back to Main Menu" + RESET)
            choice = input(MAGENTA + "👉 Enter your choice: " + RESET)
            if choice == "1":
                backup_online_data(self.db_manager)
                input("\nPress Enter to continue...")
            elif choice == "2":
                restore_online_data(self.db_manager)
                input("\nPress Enter to continue...")
            elif choice == "3":
                break
            else:
                print(RED + "❌ Invalid choice! Try again." + RESET)
                input()

    def password_menu(self, username):
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            UI.print_heading("passmenu")
            print(CYAN + "1.  Add Password" + RESET)
            print(CYAN + "2.  Access Passwords" + RESET)
            print(CYAN + "3.  Edit Password" + RESET)
            print(CYAN + "4.  Delete Password" + RESET)
            print(CYAN + "5.  List Platforms" + RESET)
            print(CYAN + "6.  Check Password Health" + RESET)
            print(CYAN + "7.  Logout" + RESET)
            choice = input(MAGENTA + "👉 Enter your choice: " + RESET)
            if choice == "1":
                self.password_manager.add_password(username)
            elif choice == "2":
                self.password_manager.access_passwords(username)
            elif choice == "3":
                self.password_manager.edit_password(username)
            elif choice == "4":
                self.password_manager.delete_password(username)
            elif choice == "5":
                self.password_manager.show_listed_platforms(username)
            elif choice == "6":
                self.password_manager.check_password_health(username)
            elif choice == "7":
                break
            else:
                print(RED + "❌ Invalid choice! Try again." + RESET)
            input()

    def run(self):
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            UI.print_heading("main")
            print(CYAN + "1.  Signup" + RESET)
            print(CYAN + "2.  Login" + RESET)
            print(CYAN + "3.  List Users" + RESET)
            print(CYAN + "4.  Delete Account" + RESET)
            print(CYAN + "5.  Backup & Restore" + RESET)
            print(CYAN + "6.  Exit" + RESET)
            choice = input(MAGENTA + "👉 Enter your choice: " + RESET)
            if choice == "1":
                self.user_manager.signup()
            elif choice == "2":
                username = self.user_manager.login()
                if username:
                    # Automatically back up online after login if internet is available.
                    backup_online_data(self.db_manager)
                    self.password_menu(username)
            elif choice == "3":
                self.user_manager.list_users()
            elif choice == "4":
                self.user_manager.delete_account()
            elif choice == "5":
                self.backup_restore_menu()
            elif choice == "6":
                print(GREEN + "🚪 Exiting... Goodbye!" + RESET)
                break
            else:
                print(RED + "❌ Invalid choice! Try again." + RESET)
            input()

if __name__ == "__main__":
    # Initialize Firebase for online backup/restore
    init_firebase()
    app = Application(DB_FILE)
    app.run()
