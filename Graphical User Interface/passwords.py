import sys
import os
import sqlite3
import hashlib
import csv
import socket
import secrets
import string
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, firestore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QInputDialog, QFormLayout, QGroupBox
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

# --------------------
# Encryption Utilities
# --------------------
def load_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)
    return key

KEY = load_key()
cipher = Fernet(KEY)

def encrypt_data(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt_data(data: bytes) -> str:
    return cipher.decrypt(data).decode()

# --------------------
# Password Strength & Generation
# --------------------
def check_password_strength(password: str) -> str:
    score = 0
    if len(password) >= 8: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1
    if score <= 2:
        return "Weak"
    elif score == 3:
        return "Medium"
    elif score == 4:
        return "Strong"
    else:
        return "Very Strong"

# --------------------
# Database Manager
# --------------------
class DatabaseManager:
    def __init__(self, path="database.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            security_q BLOB NOT NULL,
            security_a BLOB NOT NULL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            platform TEXT NOT NULL,
            platform_user TEXT NOT NULL,
            email TEXT NOT NULL,
            pwd BLOB NOT NULL,
            FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE
        )''')
        self.conn.commit()

    def close(self):
        self.conn.close()

# --------------------
# Firebase Init
# --------------------
db_online = None
def init_firebase():
    global db_online
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db_online = firestore.client()
    except Exception:
        db_online = None

# --------------------
# Internet Check
# --------------------
def internet_available(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

# --------------------
# Business Logic
# --------------------
class UserManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def hash_password(self, pwd: str) -> str:
        return hashlib.sha256(pwd.encode()).hexdigest()

    def signup(self, username: str, password: str, question: str, answer: str) -> bool:
        c = self.db.conn.cursor()
        c.execute("SELECT 1 FROM users WHERE username=?", (username,))
        if c.fetchone(): return False
        pwd_hash = self.hash_password(password)
        enc_q = encrypt_data(question)
        enc_a = encrypt_data(answer)
        c.execute("INSERT INTO users(username,password,security_q,security_a) VALUES(?,?,?,?)",
                  (username, pwd_hash, enc_q, enc_a))
        self.db.conn.commit()
        return True

    def login(self, username: str, password: str) -> bool:
        c = self.db.conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if not row: return False
        return row[0] == self.hash_password(password)

    def get_security(self, username: str):
        c = self.db.conn.cursor()
        c.execute("SELECT security_q, security_a FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if not row: return None
        return (decrypt_data(row[0]), decrypt_data(row[1]))

    def reset_password(self, username: str, new_password: str) -> bool:
        c = self.db.conn.cursor()
        c.execute("SELECT 1 FROM users WHERE username=?", (username,))
        if not c.fetchone(): return False
        c.execute("UPDATE users SET password=? WHERE username=?",
                  (self.hash_password(new_password), username))
        self.db.conn.commit()
        return True

    def delete_account(self, username: str) -> bool:
        c = self.db.conn.cursor()
        c.execute("DELETE FROM users WHERE username=?", (username,))
        self.db.conn.commit()
        return True

class PasswordManagerLogic:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_password(self, owner: str, platform: str, plat_user: str, email: str, pwd: str):
        c = self.db.conn.cursor()
        enc_pwd = encrypt_data(pwd)
        c.execute(
            "INSERT INTO passwords(owner,platform,platform_user,email,pwd) VALUES(?,?,?,?,?)",
            (owner, platform, plat_user, email, enc_pwd)
        )
        self.db.conn.commit()

    def list_platforms(self, owner: str):
        c = self.db.conn.cursor()
        c.execute("SELECT DISTINCT platform FROM passwords WHERE owner=?", (owner,))
        return [r[0] for r in c.fetchall()]

    def get_passwords(self, owner: str, platform: str):
        c = self.db.conn.cursor()
        c.execute("SELECT id,platform_user,email,pwd FROM passwords WHERE owner=? AND platform=?",
                  (owner, platform))
        rows = c.fetchall()
        return [(r[0], r[1], r[2], decrypt_data(r[3])) for r in rows]

    def delete_password(self, pwd_id: int):
        c = self.db.conn.cursor()
        c.execute("DELETE FROM passwords WHERE id=?", (pwd_id,))
        self.db.conn.commit()

    def update_password(self, pwd_id: int, new_user: str, new_pwd: str):
        c = self.db.conn.cursor()
        c.execute(
            "UPDATE passwords SET platform_user=?,pwd=? WHERE id=?",
            (new_user, encrypt_data(new_pwd), pwd_id)
        )
        self.db.conn.commit()

    def check_health(self, owner: str):
        c = self.db.conn.cursor()
        c.execute("SELECT platform,pwd FROM passwords WHERE owner=?", (owner,))
        results = []
        for plat, pwd_blob in c.fetchall():
            pwd = decrypt_data(pwd_blob)
            results.append((plat, check_password_strength(pwd)))
        return results

# CSV Import/Export
def export_csv(db: DatabaseManager):
    c = db.conn.cursor()
    c.execute("SELECT username,password,security_q,security_a FROM users")
    users = c.fetchall()
    with open("export_users.csv","w",newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["username","password_hash","security_q","security_a"])
        w.writerows(users)

    c.execute("SELECT id,owner,platform,platform_user,email,pwd FROM passwords")
    pwds = c.fetchall()
    with open("export_passwords.csv","w",newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["id","owner","platform","platform_user","email","pwd"])
        w.writerows(pwds)

def import_csv(db: DatabaseManager):
    c = db.conn.cursor()
    c.execute("DELETE FROM passwords")
    c.execute("DELETE FROM users")
    db.conn.commit()
    with open("export_users.csv",newline='',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            c.execute(
                "INSERT INTO users(username,password,security_q,security_a) VALUES(?,?,?,?)",
                (row['username'], row['password_hash'], row['security_q'], row['security_a'])
            )
    with open("export_passwords.csv",newline='',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            c.execute(
                "INSERT INTO passwords(id,owner,platform,platform_user,email,pwd) VALUES(?,?,?,?,?,?)",
                (row['id'], row['owner'], row['platform'], row['platform_user'], row['email'], row['pwd'])
            )
    db.conn.commit()

# Firebase Backup/Restore
def backup_online(db: DatabaseManager):
    global db_online
    if not db_online or not internet_available(): return False
    c = db.conn.cursor()
    c.execute("SELECT username,password,security_q,security_a FROM users")
    users = [dict(username=r[0],password=r[1],security_q=r[2],security_a=r[3]) for r in c.fetchall()]
    c.execute("SELECT id,owner,platform,platform_user,email,pwd FROM passwords")
    pwds = [dict(id=r[0],owner=r[1],platform=r[2],platform_user=r[3],email=r[4],pwd=r[5]) for r in c.fetchall()]
    db_online.collection('db_backup').document('backup').set({'users':users,'passwords':pwds})
    return True

def restore_online(db: DatabaseManager):
    global db_online
    if not db_online or not internet_available(): return False
    doc = db_online.collection('db_backup').document('backup').get()
    if not doc.exists: return False
    data = doc.to_dict()
    c = db.conn.cursor()
    c.execute("DELETE FROM passwords")
    c.execute("DELETE FROM users")
    for u in data['users']:
        c.execute(
            "INSERT INTO users(username,password,security_q,security_a) VALUES(?,?,?,?)",
            (u['username'], u['password'], u['security_q'], u['security_a'])
        )
    for p in data['passwords']:
        c.execute(
            "INSERT INTO passwords(id,owner,platform,platform_user,email,pwd) VALUES(?,?,?,?,?,?)",
            (p['id'], p['owner'], p['platform'], p['platform_user'], p['email'], p['pwd'])
        )
    db.conn.commit()
    return True

# --------------------
# PyQt5 GUI
# --------------------
class SecureManagerGUI(QWidget):
    def __init__(self):
        super().__init__()
        init_firebase()
        self.db = DatabaseManager()
        self.user_logic = UserManager(self.db)
        self.pwd_logic = PasswordManagerLogic(self.db)
        self.current_user = None
        self.setWindowTitle("Secure Password Manager")
        self.resize(1000, 700)
        self.apply_theme()
        self.build_ui()

    def apply_theme(self):
        # global black/green theme
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(0,0,0))
        pal.setColor(QPalette.WindowText, QColor(0,255,0))
        self.setPalette(pal)
        # widget stylesheet
        self.setStyleSheet("""
            QWidget { background-color: #000; color: #0f0; font-family: Consolas; }
            QLineEdit, QTextEdit, QTableWidget, QListWidget {
                background-color: #000; color: #0f0;
                border: 1px solid #0f0; border-radius: 4px;
            }
            QPushButton {
                background-color: transparent; color: #0f0;
                border: 1px solid #0f0; border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #003300; }
            QHeaderView::section {
                background-color: #000; color: #0f0;
                border: 1px solid #0f0;
            }
            QTableWidget::item {
                selection-background-color: #033; selection-color: #0f0;
            }
            QListWidget::item:selected {
                background-color: #033; color: #0f0;
            }
        """)

    def build_ui(self):
        self.stack = QStackedWidget()
        v = QVBoxLayout(self)
        v.addWidget(self.stack)

        self.login_screen = self.screen_login()
        self.signup_screen = self.screen_signup()
        self.dashboard = self.screen_dashboard()
        self.pwd_screen = self.screen_passwords()
        self.backup_screen = self.screen_backup()
        self.csv_screen = self.screen_csv()

        for w in [self.login_screen, self.signup_screen, self.dashboard,
                  self.pwd_screen, self.backup_screen, self.csv_screen]:
            self.stack.addWidget(w)

        self.stack.setCurrentWidget(self.login_screen)

    # -- Login Screen --
    def screen_login(self):
        w = QWidget()
        form = QFormLayout()
        lbl = QLabel("Login"); lbl.setFont(QFont('Consolas',24))
        form.addRow(lbl)
        self.login_user = QLineEdit(); self.login_user.setPlaceholderText("Username")
        form.addRow("User:", self.login_user)
        self.login_pwd = QLineEdit(); self.login_pwd.setEchoMode(QLineEdit.Password)
        self.login_pwd.setPlaceholderText("Password")
        form.addRow("Password:", self.login_pwd)
        btn_login = QPushButton("Login"); btn_login.clicked.connect(self.do_login)
        btn_to_signup = QPushButton("Sign Up")
        btn_to_signup.clicked.connect(lambda: self.stack.setCurrentWidget(self.signup_screen))
        h = QHBoxLayout(); h.addWidget(btn_login); h.addWidget(btn_to_signup)
        form.addRow(h)
        w.setLayout(form)
        return w

    def do_login(self):
        u = self.login_user.text().strip()
        p = self.login_pwd.text()
        if self.user_logic.login(u,p):
            self.current_user = u
            backup_online(self.db)
            self.refresh_password_list()
            self.stack.setCurrentWidget(self.dashboard)
            self.login_user.clear(); self.login_pwd.clear()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

    # -- Signup Screen --
    def screen_signup(self):
        w = QWidget()
        form = QFormLayout()
        lbl = QLabel("Sign Up"); lbl.setFont(QFont('Consolas',24))
        form.addRow(lbl)
        self.su_user = QLineEdit(); self.su_user.setPlaceholderText("Username")
        form.addRow("User:", self.su_user)
        self.su_pwd = QLineEdit(); self.su_pwd.setEchoMode(QLineEdit.Password)
        self.su_pwd.setPlaceholderText("Password")
        form.addRow("Password:", self.su_pwd)
        self.su_q = QLineEdit(); self.su_q.setPlaceholderText("Security Question")
        form.addRow("Question:", self.su_q)
        self.su_a = QLineEdit(); self.su_a.setPlaceholderText("Answer")
        form.addRow("Answer:", self.su_a)
        btn_create = QPushButton("Create"); btn_create.clicked.connect(self.do_signup)
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_screen))
        h = QHBoxLayout(); h.addWidget(btn_create); h.addWidget(btn_back)
        form.addRow(h)
        w.setLayout(form); return w

    def do_signup(self):
        u,p,q,a = self.su_user.text().strip(), self.su_pwd.text(), self.su_q.text(), self.su_a.text()
        if not u or not p or not q or not a:
            QMessageBox.warning(self, "Error", "All fields required.")
            return
        if self.user_logic.signup(u,p,q,a):
            QMessageBox.information(self, "Success", "Account created.")
            self.stack.setCurrentWidget(self.login_screen)
            self.su_user.clear(); self.su_pwd.clear(); self.su_q.clear(); self.su_a.clear()
        else:
            QMessageBox.warning(self, "Error", "Username exists.")

    # -- Dashboard --
    def screen_dashboard(self):
        w = QWidget(); v = QVBoxLayout()
        for text, func in [
            ("Manage Passwords", lambda:self.stack.setCurrentWidget(self.pwd_screen)),
            ("Backup/Restore", lambda:self.stack.setCurrentWidget(self.backup_screen)),
            ("CSV Import/Export", lambda:self.stack.setCurrentWidget(self.csv_screen)),
            ("Logout", self.do_logout)
        ]:
            btn = QPushButton(text); btn.clicked.connect(func)
            btn.setFont(QFont('Consolas',16)); v.addWidget(btn)
        w.setLayout(v); return w

    def do_logout(self):
        self.current_user = None
        self.stack.setCurrentWidget(self.login_screen)

    # -- Password Manager Screen --
    def screen_passwords(self):
        w = QWidget(); v = QVBoxLayout(); h = QHBoxLayout()
        self.platform_list = QListWidget(); self.platform_list.clicked.connect(self.on_platform_select)
        self.pwd_table = QTableWidget(0,4)
        self.pwd_table.setHorizontalHeaderLabels(["ID","User","Email","Password"])
        h.addWidget(self.platform_list,1); h.addWidget(self.pwd_table,3)
        v.addLayout(h)
        for text, func in [
            ("Add", self.on_add_pwd),
            ("Edit", self.on_edit_pwd),
            ("Delete", self.on_del_pwd),
            ("Check Health", self.on_check_health),
            ("Back", lambda:self.stack.setCurrentWidget(self.dashboard))
        ]:
            btn = QPushButton(text); btn.clicked.connect(func)
            btn.setFont(QFont('Consolas',12)); v.addWidget(btn)
        w.setLayout(v); return w

    def refresh_password_list(self):
        self.platform_list.clear()
        if self.current_user:
            for plat in self.pwd_logic.list_platforms(self.current_user):
                self.platform_list.addItem(plat)

    def on_platform_select(self):
        plat = self.platform_list.currentItem().text()
        data = self.pwd_logic.get_passwords(self.current_user, plat)
        self.pwd_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.pwd_table.setItem(i,j,QTableWidgetItem(str(val)))

    def on_add_pwd(self):
        plat, ok = QInputDialog.getText(self, "Platform", "Enter platform name:")
        if not ok or not plat: return
        user, ok = QInputDialog.getText(self, "Username", "Enter platform username:")
        if not ok or not user: return
        email, ok = QInputDialog.getText(self, "Email", "Enter email:")
        if not ok or not email: return
        pwd, ok = QInputDialog.getText(self, "Password", "Enter password:")
        if not ok or not pwd: return
        self.pwd_logic.add_password(self.current_user, plat, user, email, pwd)
        self.refresh_password_list()

    def on_edit_pwd(self):
        row = self.pwd_table.currentRow()
        if row < 0: return
        pwd_id = int(self.pwd_table.item(row,0).text())
        new_user, ok = QInputDialog.getText(self, "Edit User", "New platform user:")
        if not ok: return
        new_pwd, ok = QInputDialog.getText(self, "Edit Password", "New password:")
        if not ok: return
        self.pwd_logic.update_password(pwd_id, new_user, new_pwd)
        self.on_platform_select()

    def on_del_pwd(self):
        row = self.pwd_table.currentRow()
        if row < 0: return
        pwd_id = int(self.pwd_table.item(row,0).text())
        self.pwd_logic.delete_password(pwd_id)
        self.on_platform_select()

    def on_check_health(self):
        results = self.pwd_logic.check_health(self.current_user)
        msg = "\n".join([f"{r[0]}: {r[1]}" for r in results])
        QMessageBox.information(self, "Health Check", msg)

    # -- Backup/Restore Screen --
    def screen_backup(self):
        w = QWidget(); v = QVBoxLayout()
        for text, func in [
            ("Backup Online", self.do_backup),
            ("Restore Online", self.do_restore),
            ("Back", lambda:self.stack.setCurrentWidget(self.dashboard))
        ]:
            btn = QPushButton(text); btn.clicked.connect(func)
            btn.setFont(QFont('Consolas',14)); v.addWidget(btn)
        w.setLayout(v); return w

    def do_backup(self):
        ok = backup_online(self.db)
        QMessageBox.information(self, "Backup", "Backup successful." if ok else "Backup failed.")

    def do_restore(self):
        ok = restore_online(self.db)
        QMessageBox.information(self, "Restore", "Restore successful." if ok else "Restore failed.")

    # -- CSV Screen --
    def screen_csv(self):
        w = QWidget(); v = QVBoxLayout()
        for text, func in [
            ("Export CSV", lambda: (export_csv(self.db), QMessageBox.information(self,"CSV","Export done"))),
            ("Import CSV", lambda: (import_csv(self.db), QMessageBox.information(self,"CSV","Import done"))),
            ("Back", lambda:self.stack.setCurrentWidget(self.dashboard))
        ]:
            btn = QPushButton(text); btn.clicked.connect(func)
            btn.setFont(QFont('Consolas',14)); v.addWidget(btn)
        w.setLayout(v); return w

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SecureManagerGUI()
    gui.show()
    sys.exit(app.exec_())
