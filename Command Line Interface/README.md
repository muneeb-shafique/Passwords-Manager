<html>
<body>

  <header>
    <h1>⭐ Secure Password Manager System ⭐</h1>
    <p>A secure, multi-user password management system with enhanced encryption, online backup, CSV import/export, and privacy.</p>
  </header>

  <section>
    <h2>Overview</h2>
    <p>
      This Password Manager allows multiple users to securely store and manage passwords for various online platforms.
      It features user registration, login, password storage, account deletion, <strong>CSV import/export</strong>, and an <strong>online backup &amp; restore</strong> functionality.
      The application uses SHA-256 for user password hashing and Fernet encryption to secure platform passwords.
    </p>
    <ul>
      <li><strong>User Registration &amp; Login:</strong> Sign up, log in, and delete accounts securely. At any prompt, type <strong>"back"</strong> to return to the main menu.</li>
      <li>
        <strong>Password Management:</strong> Add, access, edit, and delete passwords for various platforms. You can type <strong>"auto"</strong> for auto-generated passwords or <strong>"back"</strong> to cancel.
      </li>
      <li><strong>CSV Import/Export:</strong> Export your entire local database to CSV files (`export_users.csv` &amp; `export_passwords.csv`) or import from those CSVs—perfect for offline backups or migrations.</li>
      <li><strong>Encryption:</strong> All passwords are securely protected using SHA-256 for user credentials and Fernet for platform passwords.</li>
      <li><strong>Multi-user Support:</strong> Each user’s data is stored separately for enhanced security.</li>
      <li>
        <strong>Data Storage:</strong> User credentials and platform data are stored in an SQLite3 database file (.db). An integrated online backup and restore feature allows you to store your entire database securely on Firebase Firestore.
      </li>
      <li>
        <strong>Password Strength Checker:</strong> Evaluate password strength during creation or update with real-time feedback.
      </li>
      <li>
        <strong>Auto Password Generation:</strong> When prompted for a password, type <strong>"auto"</strong> to generate a strong, random password automatically.
      </li>
    </ul>
  </section>

  <section>
    <h2>User Management</h2>
    <p>
      Manage user signups, logins, and account deletions. Each user's credentials and saved data are protected with robust encryption.
      Prompts guide you with options to type <strong>"back"</strong> to return to the main menu whenever needed.
    </p>
    <table border="1">
      <thead>
        <tr>
          <th>Action</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Signup</td>
          <td>
            Register with a unique username and secure password (encrypted, strength checked, auto-generation available, and "back" to cancel).
          </td>
        </tr>
        <tr>
          <td>Login</td>
          <td>Access your account securely using your credentials (or type "back" to return to the main menu).</td>
        </tr>
        <tr>
          <td>Delete Account</td>
          <td>Remove your account and all associated data from the system (with a "back" option to cancel the process).</td>
        </tr>
      </tbody>
    </table>
  </section>

  <section>
    <h2>Password Management</h2>
    <p>
      Securely add, view, edit, and delete passwords for different platforms. All sensitive data is encrypted and stored safely.
      At each prompt, instructions specify that you can type <strong>"back"</strong> to return to the main menu or <strong>"auto"</strong> to generate a password automatically.
    </p>
    <table border="1">
      <thead>
        <tr>
          <th>Action</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Add Password</td>
          <td>
            Enter new credentials for various online platforms. Passwords are checked for strength before being saved, with options to auto-generate ("auto") or cancel ("back").
          </td>
        </tr>
        <tr>
          <td>Access Passwords</td>
          <td>Retrieve stored passwords by entering the platform's name (or "back" to return).</td>
        </tr>
        <tr>
          <td>Edit Password</td>
          <td>
            Update existing credentials with password strength re-evaluation and options for auto-generation ("auto") or canceling ("back").
          </td>
        </tr>
        <tr>
          <td>Delete Password</td>
          <td>Remove credentials for platforms no longer in use (with an option to type "back" to cancel).</td>
        </tr>
        <tr>
          <td>List Platforms</td>
          <td>View all platforms for which passwords are saved.</td>
        </tr>
      </tbody>
    </table>
  </section>

  <section>
    <h2>CSV Import/Export</h2>
    <p>
      Easily export your local SQLite data into two CSV files:
    </p>
    <ul>
      <li><code>export_users.csv</code>: Contains all user records (username, password hash, encrypted security Q&A).</li>
      <li><code>export_passwords.csv</code>: Contains all password entries (id, username, platform, platform_username, email, encrypted password).</li>
    </ul>
    <p>
      You can also import from those CSVs to replace the local database, making migrations or offline backups a breeze.
    </p>
  </section>

  <section>
    <h2>Online Backup &amp; Restore</h2>
    <p>
      This feature allows you to backup your entire local database (including user data and saved passwords) to Firebase Firestore.
      You can also restore the backup to recover your data if needed. The backup and restore options are available from the main menu.
    </p>
    <ul>
      <li>
        <strong>Online Backup:</strong> When an internet connection is available, your entire database is automatically backed up upon login.
      </li>
      <li>
        <strong>Online Restore:</strong> If needed, restore the database from the online backup. This process will replace your current local data.
      </li>
    </ul>
    <p>
      <strong>Note:</strong> For security, your Firebase credentials (serviceAccountKey.json) must not be committed to the public repository.
      Instead, add the file to your .gitignore and follow the instructions below to set up your own Firebase project.
    </p>
  </section>

  <section>
    <h2>Firebase Setup (For Online Backup)</h2>
    <p>
      To enable online backup and restore, follow these steps to add your own Firebase database:
    </p>
    <ol>
      <li>
        Go to the <a href="https://console.firebase.google.com/">Firebase Console</a> and create a new project.
      </li>
      <li>
        Navigate to <strong>Project Settings &gt; Service accounts</strong> and click <strong>"Generate new private key"</strong> to download your <code>serviceAccountKey.json</code> file.
      </li>
      <li>
        Place the <code>serviceAccountKey.json</code> file in your project directory and add it to your <code>.gitignore</code> file to keep it private.
      </li>
      <li>
        Install the Firebase Admin SDK by running: <br>
        <code>pip install firebase-admin</code>
      </li>
    </ol>
  </section>

  <section>
    <h2>Password Strength Checker</h2>
    <p>
      This feature evaluates the strength of your passwords in real-time by checking:
    </p>
    <ul>
      <li><strong>Minimum Length:</strong> At least 8 characters.</li>
      <li><strong>Character Variety:</strong> Inclusion of lowercase, uppercase, numeric, and special characters.</li>
      <li><strong>Strength Rating:</strong> Passwords are classified as Weak, Medium, Strong, or Very Strong.</li>
    </ul>
  </section>

  <section>
    <h2>Security &amp; Encryption</h2>
    <p>
      User credentials are hashed with SHA-256, and platform passwords are encrypted with Fernet symmetric encryption.
      This ensures that even if data is compromised, your sensitive information remains secure.
    </p>
    <h3>Data Storage Format</h3>
    <p>
      All data is stored in an SQLite3 database (.db), which can be easily backed up and restored without compromising security.
    </p>
  </section>

  <section>
    <h2>Getting Started</h2>
    <h3>Clone the Repository</h3>
    <p>Clone the repository to your local machine using the following command:</p>
    <pre>git clone https://github.com/muneeb-shafique/Passwords-Manager/</pre>

 <h3>Install Required Modules</h3>
    <p>Install the required modules using pip:</p>
    <pre>pip install pwinput firebase-admin cryptography</pre>

 <h3>Firebase Setup</h3>
    <p>
      Follow the Firebase Setup instructions above to obtain your <code>serviceAccountKey.json</code> file. Ensure this file is added to your <code>.gitignore</code> to keep your credentials secure.
    </p>

  <h3>Project Demo</h3>
    <p>Watch the demo to see the project in action:</p>
    <img src="Preview/demo.gif" alt="Project Demo">
  </section>

  <section>
    <h2>How It Works</h2>
    <ol>
      <li>
        <strong>Signup:</strong> Create a new account with a username and secure password. Type <strong>"auto"</strong> to auto-generate a password or <strong>"back"</strong> to cancel.
      </li>
      <li>
        <strong>Login:</strong> Access your account to manage your stored passwords (or type <strong>"back"</strong> to return to the main menu).
      </li>
      <li>
        <strong>Password Management:</strong> Add, edit, view, or delete credentials for different platforms. At any step, use <strong>"auto"</strong> for password generation or <strong>"back"</strong> to cancel.
      </li>
      <li>
        <strong>CSV Import/Export:</strong> From the main menu select <strong>“CSV Import/Export”</strong> to export your data to CSV files or import from them.
      </li>
      <li>
        <strong>Online Backup &amp; Restore:</strong> Backup your entire database to Firebase automatically upon login (if online) or manually via the main menu.
      </li>
      <li>
        <strong>Logout:</strong> Securely log out when you’re finished.
      </li>
    </ol>
  </section>

  <section>
    <h2>Conclusion</h2>
    <p>
      The Secure Password Manager System provides a professional and intuitive solution for managing your online credentials.
      With strong encryption, a user-friendly interface, real-time password strength checking, built-in auto password generation, CSV import/export, and an online backup/restore feature, you can be confident that your data is both secure and easily manageable.
    </p>
    <p>
      Explore, contribute, and enjoy enhanced security for all your password management needs.
    </p>
  </section>

  <footer>
    <p>&copy; 2025 Secure Password Manager. All Rights Reserved.</p>
  </footer>

</body>
</html>
