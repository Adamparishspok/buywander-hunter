# User Accounts

This app now supports multiple user accounts. Here are the default credentials:

## Adam's Account
- **Username:** `Adam`
- **Password:** `adam123`
- **Initials:** AP

## Alex's Account
- **Username:** `Alex`
- **Password:** `alex123`
- **Initials:** AP

## Changing Passwords

To change passwords, you can edit the `users.json` file that will be created when you first run the app.

The passwords are hashed using SHA256, so if you want to set a new password:

1. Generate a hash using Python:
```python
import hashlib
password = "your_new_password"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

2. Update the password field in `users.json` with the hash.

## Notes

- Usernames are case-sensitive (use exact capitalization: "Adam" and "Alex")
- Both users share the same interests and scraping data
- Each user sees their own name in the sidebar when logged in
