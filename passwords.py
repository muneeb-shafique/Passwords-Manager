import hashlib
import json
import os
import pwinput


BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
RESET = "\033[0m"

data_file = "users.json"
passwords_file = "passwords.json"

class UserManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                return json.load(file)
        return {}

    def save_users(self):
        with open(self.data_file, "w") as file:
            json.dump(self.users, file, indent=4)

    def encrypt_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()


    def signup(self):
        os.system("cls")
        UI.print_heading("signup")
        username = input(GREEN + "📝  Enter username: " + RESET)
        if username.lower() == "back":
            return
        elif not username.isalnum():
            input(RED + "❌ Please enter a valid username." + RESET)
            self.signup()
        if username in self.users:
            input(RED + "❌ Username already exists! Try another." + RESET)
            self.signup()
        password = UserManager.get_password(GREEN + "🔒  Enter password: " + RESET)
        if not password:
            input(RED + "❌ Please enter a valid password." + RESET)
            self.signup()
        confirm = input(YELLOW + f"\nYour password is: {GREEN}{password}{YELLOW}. Do you confirm this password?  " + RESET)
        if confirm.lower() == "yes" or confirm.lower() == "y":
            security_question = input(YELLOW + "🔐 Set a security question (e.g., Your pet's name?): " + RESET)
            security_answer = input(YELLOW + "🔑 Answer: " + RESET).lower()
            self.users[username] = {"password": self.encrypt_password(password), "security_question": security_question, "security_answer": security_answer}
            self.save_users()
            print("\n" + GREEN + "✅ Signup successful!" + RESET)
        elif confirm.lower() == "no" or confirm.lower() == "n":
            input(RED + "❌ Please Enter password again! Press enter to continue." + RESET)
            self.signup()
        else:
            input(RED + "❌ Invalid Input!" + RESET)
            self.signup()


    @staticmethod
    def get_password(txt):
        return pwinput.pwinput(prompt=txt)


    def list_users(self):
        os.system("cls")
        UI.print_heading("listusers")
        if self.users:
            print(CYAN,end="")
            for i, user in enumerate(self.users.keys(), 1):
                print(f"{i}. {user}")
            print(RESET)
        else:
            print(RED + "❌ No users found!" + RESET)
        input("\nPress Enter to continue...")


    def login(self):
        os.system("cls")
        UI.print_heading("login")
        print("[NOTE]: Press F Key in case of forgetting password.")
        username = input(BLUE + "👤 Enter username: " + RESET)
        if username.lower()=="f":
            self.forget_password()
        if username.lower() == "back":
            return
        password = self.get_password(BLUE + "🔑 Enter password: " + RESET)
        if "password" not in self.users[username]:
            input("\n⚠️ User data is corrupted. Contact support!")
            return None
        if username in self.users and self.users[username]["password"] == self.encrypt_password(password):
            print("\n" + GREEN + "✅ Login successful! Welcome back!" + RESET)
            return username
        else:
            input("\n" + RED + "❌ Invalid username or password!" + RESET)
            return None

    def forget_password(self):
        os.system("cls")
        UI.print_heading("forgetpass")
        username = input(YELLOW + "👤 Enter your username: " + RESET)
        if username in self.users:
            print(YELLOW + "Q: "+ self.users[username]["security_question"] + RESET)
            answer = input(YELLOW + "🔑 Answer: " + RESET).lower()
            if answer == self.users[username]["security_answer"]:
                new_password = UserManager.get_password(GREEN + "🔒 Enter new password: " + RESET)
                self.users[username]["password"] = self.encrypt_password(new_password)
                self.save_users()
                input(GREEN + "✅ Password reset successful!" + RESET)
            else:
                input(RED + "❌ Incorrect answer!" + RESET)
        else:
            input(RED + "❌ Username not found!" + RESET)
        self.login()
        

    def delete_account(self):
        os.system("cls")
        UI.print_heading("delacc")
        username = input(YELLOW + "🗑️  Enter username: " + RESET)
        if username.lower() == "back":
            return
        password = self.get_password(YELLOW + "🔑  Enter password: " + RESET)
        if username in self.users and self.users[username] == self.encrypt_password(password):
            confirm = input(YELLOW + f"\nAll your saved passwords will be removed. Are you sure you want to continue?  " + RESET)
            if confirm.lower() == "yes" or confirm.lower() == "y":
                del self.users[username]
                self.save_users()
            elif confirm.lower() == "no" or confirm.lower() == "n":
                input(RED + "❌ Deletion of Account canceled." + RESET)
                self.signup()
            else:
                input(RED + "❌ Invalid Input!" + RESET)
                self.signup()
        else:
            print(RED + "❌ Invalid username or password!" + RESET)

class PasswordManager:
    def __init__(self, passwords_file):
        self.passwords_file = passwords_file
        self.passwords = self.load_passwords()

    def load_passwords(self):
        if os.path.exists(self.passwords_file):
            with open(self.passwords_file, "r") as file:
                return json.load(file)
        return {}

    def save_passwords(self):
        with open(self.passwords_file, "w") as file:
            json.dump(self.passwords, file, indent=4)

    def add_password(self, username):
        os.system("cls")
        UI.print_heading("addpass")
        platform = (input(GREEN + "🌐 Enter platform name: " + RESET)).lower()
        platform_username = input(GREEN + "👤 Enter username: " + RESET)
        email = input(GREEN + "📧 Enter email: " + RESET)
        password = UserManager.get_password(GREEN + "🔒 Enter password: " + RESET)
        confirm = input(YELLOW + f"\nYour password is: {GREEN}{password}{YELLOW}. Do you confirm this password?  " + RESET)
        if confirm.lower() == "yes" or confirm.lower() == "y":
            if username not in self.passwords:
                self.passwords[username] = {}
                self.passwords[username][platform] = {"username": platform_username, "email": email, "password": password}
                self.save_passwords()
                print(GREEN + "✅ Password saved!" + RESET)
        elif confirm.lower() == "no" or confirm.lower() == "n":
            input(RED + "❌ Please Enter password again! Press enter to continue." + RESET)
            self.signup()
        else:
            input(RED + "❌ Invalid Input!" + RESET)
            self.signup()

    def access_passwords(self, username):
        os.system("cls")
        UI.print_heading("accesspass")
        platform = (input(CYAN + "🔎 Enter platform name: " + RESET)).lower()
        if username in self.passwords and platform in self.passwords[username]:
            creds = self.passwords[username][platform]
            print(CYAN + f"Platform: {platform}\nUsername: {creds['username']}\nEmail: {creds['email']}\nPassword: {creds['password']}" + RESET)
        else:
            print(RED + "❌ No saved credentials for this platform!" + RESET)

    def delete_password(self, username):
        os.system("cls")
        UI.print_heading("delpass")
        platform = (input(YELLOW + "🗑️ Enter platform name to delete: " + RESET)).lower()
        if username in self.passwords and platform in self.passwords[username]:
            del self.passwords[username][platform]
            self.save_passwords()
            print(GREEN + "✅ Password deleted!" + RESET)
        else:
            print(RED + "❌ No such password found!" + RESET)
    
    def edit_password(self, username):
        os.system("cls")
        UI.print_heading("editpass")
        platform = (input(YELLOW + "✏️ Enter platform name to edit: " + RESET)).lower()
        if username in self.passwords and platform in self.passwords[username]:
            platform_username = input(YELLOW + "👤 Enter new username: " + RESET)
            password = input(YELLOW + "🔒 Enter new password: " + RESET)
            self.passwords[username][platform]["username"] = platform_username
            self.passwords[username][platform]["password"] = password
            self.save_passwords()
            print(GREEN + "✅ Password updated successfully!" + RESET)
        else:
            print(RED + "❌ No saved credentials for this platform!" + RESET)
    
    def show_listed_platforms(self, username):
        os.system("cls")
        UI.print_heading("showplat")
        i=0
        if username in self.passwords:
            for platform in self.passwords[username]:
                i+=1
                print(CYAN + f"{i}. {platform.title()}" + RESET)
        else:
            print(RED + "❌ No saved platforms found!" + RESET)

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


class Application:
    def __init__(self):
        self.user_manager = UserManager(data_file)
        self.password_manager = PasswordManager(passwords_file)

    def password_menu(self, username):
        while True:
            os.system("cls")
            UI.print_heading("passmenu")
            print(CYAN + "1.  Add Password" + RESET)
            print(CYAN + "2.  Access Passwords" + RESET)
            print(CYAN + "3.  Edit Password" + RESET)
            print(CYAN + "4.  Delete Password" + RESET)
            print(CYAN + "5.  List Platforms" + RESET)
            print(CYAN + "6.  Logout" + RESET)
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
                break
            else:
                print(RED + "❌ Invalid choice! Try again." + RESET)
            input()
        

    def run(self):
        while True:
            os.system("cls")
            UI.print_heading("main")
            print(CYAN + "1.  Signup" + RESET)
            print(CYAN + "2.  Login" + RESET)
            print(CYAN + "3.  List Users" + RESET)
            print(CYAN + "4.  Delete Account" + RESET)
            print(CYAN + "5.  Exit" + RESET)
            choice = input(MAGENTA + "👉 Enter your choice: " + RESET)
            if choice == "1":
                self.user_manager.signup()
            elif choice == "2":
                username = self.user_manager.login()
                if username:
                    self.password_menu(username)
            elif choice == "3":
                self.user_manager.list_users()
            elif choice == "4":
                self.user_manager.delete_account()
            elif choice=="5":
                print(GREEN + "🚪 Exiting... Goodbye!" + RESET)
                break
            else:
                print(RED + "❌ Invalid choice! Try again." + RESET)
            input()

if __name__ == "__main__":
    app = Application()
    app.run()