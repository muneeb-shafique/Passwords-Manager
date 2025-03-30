<html>
<body>

  <header>
    <h1>⭐ Secure Password Manager System ⭐</h1>
    <p>A secure, multi-user password management system with enhanced encryption and privacy.</p>
  </header>

  <section>
    <h2>Overview</h2>
    <p>
      This Password Manager allows multiple users to securely store and manage passwords for various online platforms.
      It features user registration, login, password storage, and account deletion, all with the highest level of encryption.
      The application uses SHA-256 for user password hashing and Fernet encryption to secure platform passwords.
    </p>
    <ul>
      <li>User Registration &amp; Login: Sign up, log in, and delete accounts securely. Prompts include an option to type <strong>"back"</strong> to return to the main menu.</li>
      <li>Password Management: Add, access, edit, and delete passwords for various platforms. At any input prompt, you can type <strong>"back"</strong> to go back to the main menu.</li>
      <li>Encryption: All passwords are securely protected using SHA-256 and Fernet encryption.</li>
      <li>Multi-user Support: Each user’s data is stored separately for enhanced security.</li>
      <li>Data Storage: Passwords and user data are stored in an SQLite3 database file (.db) for easy backup and management.</li>
      <li>Password Strength Checker: Evaluate password strength during creation or update to ensure robust security.</li>
      <li>Auto Password Generation: When prompted for a password, users can type <strong>"auto"</strong> to have the system generate a strong, random password automatically.</li>
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
            Register with a unique username and secure password (encrypted, strength checked, auto-generated option available, and "back" to cancel).
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
      At each prompt, instructions specify that you can type <strong>"back"</strong> to return to the main menu, and you may also use <strong>"auto"</strong> to generate a password automatically.
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
            Enter new credentials for various online platforms. Passwords are checked for strength before being saved, and you can type "auto" to generate a strong password, or "back" to cancel.
          </td>
        </tr>
        <tr>
          <td>Access Passwords</td>
          <td>Retrieve stored passwords by entering the platform's name (or "back" to return).</td>
        </tr>
        <tr>
          <td>Edit Password</td>
          <td>
            Update existing credentials as necessary, with password strength re-evaluation and options for auto-generation or canceling ("back").
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
    <h2>Password Strength Checker</h2>
    <p>
      A feature that evaluates the strength of your passwords in real-time. The system checks for:
    </p>
    <ul>
      <li><strong>Minimum Length:</strong> At least 8 characters.</li>
      <li><strong>Character Variety:</strong> Inclusion of lowercase, uppercase, numeric, and special characters.</li>
      <li><strong>Strength Rating:</strong> Passwords are classified as Weak, Medium, Strong, or Very Strong.</li>
    </ul>
    <p>
      This helps ensure that both your account passwords and platform credentials meet high security standards.
    </p>
  </section>

  <section>
    <h2>Security &amp; Encryption</h2>
    <p>
      All passwords are encrypted using the SHA-256 hash algorithm for user credentials and Fernet symmetric encryption for platform passwords.
      This ensures that even if data is compromised, the original passwords remain secure.
    </p>
    <h3>Data Storage Format</h3>
    <p>
      User data is stored in an SQLite3 database for efficient and structured credential management.
      The database file (.db) can be easily backed up, transferred, and restored without compromising security.
    </p>
  </section>

  <section>
    <h2>Getting Started</h2>
    <h3>Clone the Repository</h3>
    <p>Clone the repository to your local machine using the following command:</p>
    <pre>git clone https://github.com/muneeb-shafique/Passwords-Manager/</pre>
    
<h3>Install Required Modules</h3>
    <p>Install the required modules using pip:</p>
    <pre>pip install pwinput</pre>
    
<h3>Project Demo</h3>
    <p>Watch the demo to see the project in action:</p>
    <img src="Preview/demo.gif" alt="Project Demo">
  </section>

  <section>
    <h2>How It Works</h2>
    <ol>
      <li>
        <strong>Signup:</strong> Create a new account with a username and secure password. You can type "auto" to auto-generate a password or "back" to cancel.
      </li>
      <li>
        <strong>Login:</strong> Access your account to manage your stored passwords (or type "back" to return to the main menu).
      </li>
      <li>
        <strong>Password Management:</strong> Add, edit, view, or delete credentials for different platforms. At any step, type "auto" for password generation or "back" to cancel.
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
      With strong encryption, a user-friendly interface, real-time password strength checking, and built-in auto password generation along with easy navigation ("back" option), you can be confident that your data is both secure and easily manageable.
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
