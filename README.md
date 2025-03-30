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
      <li>User Registration &amp; Login: Sign up, log in, and delete accounts securely.</li>
      <li>Password Management: Add, access, edit, and delete passwords for various platforms.</li>
      <li>Encryption: All passwords are securely protected using SHA-256 and Fernet encryption.</li>
      <li>Multi-user Support: Each user’s data is stored separately for enhanced security.</li>
      <li>Data Storage: Passwords and user data are stored in an SQLite3 database file (.db) for easy backup and management.</li>
      <li>Password Strength Checker: Evaluate password strength during creation or update to ensure robust security.</li>
    </ul>
  </section>

  <section>
    <h2>User Management</h2>
    <p>
      Manage user signups, logins, and account deletions. Each user's credentials and saved data are protected with robust encryption.
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
          <td>Register with a unique username and secure password (encrypted and evaluated for strength).</td>
        </tr>
        <tr>
          <td>Login</td>
          <td>Access your account securely using your credentials.</td>
        </tr>
        <tr>
          <td>Delete Account</td>
          <td>Remove your account and all associated data from the system.</td>
        </tr>
      </tbody>
    </table>
  </section>

  <section>
    <h2>Password Management</h2>
    <p>
      Securely add, view, edit, and delete passwords for different platforms. All sensitive data is encrypted and stored safely.
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
          <td>Enter new credentials for various online platforms. Passwords are checked for strength before being saved.</td>
        </tr>
        <tr>
          <td>Access Passwords</td>
          <td>Retrieve stored passwords by entering the platform's name.</td>
        </tr>
        <tr>
          <td>Edit Password</td>
          <td>Update existing credentials as necessary, with password strength re-evaluation.</td>
        </tr>
        <tr>
          <td>Delete Password</td>
          <td>Remove credentials for platforms no longer in use.</td>
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
      A new feature to evaluate the strength of your passwords in real-time. The system checks for:
    </p>
    <ul>
      <li><strong>Minimum Length:</strong> Password must be at least 8 characters.</li>
      <li><strong>Character Variety:</strong> Inclusion of lowercase, uppercase, numeric, and special characters.</li>
      <li><strong>Strength Rating:</strong> Passwords are rated as Weak, Medium, Strong, or Very Strong.</li>
    </ul>
    <p>
      This feature helps ensure that both your user account password and the platform-specific passwords meet high security standards.
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
      User data is securely stored using an SQLite3 database, ensuring efficient and structured storage of credentials.
      This database-driven approach allows for scalable and high-performance data management, reducing redundancy and improving retrieval efficiency.
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
      <li>Signup: Create a new account with a username and secure password. The password is evaluated for strength before saving.</li>
      <li>Login: Access your account to manage your stored passwords.</li>
      <li>Password Management: Add, edit, view, or delete credentials for different platforms with continuous password strength checks.</li>
      <li>Logout: Securely log out when you’re finished.</li>
    </ol>
  </section>

  <section>
    <h2>Conclusion</h2>
    <p>
      The Secure Password Manager System provides a professional and intuitive solution for managing your online credentials.
      With strong encryption, a user-friendly interface, and a real-time password strength checker, you can be confident that your data is both secure and accessible.
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
