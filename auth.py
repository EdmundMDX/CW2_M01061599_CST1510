import bcrypt
import os
import re # regular expression module for checking characters

# Step 6. Define the User Data File
USER_DATA_FILE = "users.txt"
# Step 4. Implement the Password Hashing Function

def hash_password(plain_text_password):
   
    # TODO: Encode the password to bytes (bcrypt requires byte strings)
    password_bytes = plain_text_password.encode('utf-8')
    # TODO: Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()
    # TODO: Hash the password using bcrypt.hashpw()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    # TODO: Decode the hash back to a string to store in a text file

    return hashed_password.decode('utf-8')

# Step 5. Implement the Password Verification Function

def verify_password(plain_text_password, hashed_password):
    
    # TODO: Encode both the plaintext password and the stored hash to byt
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    # TODO: Use bcrypt.checkpw() to verify the password
    
    # This function extracts the salt from the hash and compares
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

# Step 7. Implement the Registration Function
def register_user(username, password, role="user"):
    
    # TODO: Check if the username already exists
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False
    # TODO: Hash the password
    hashed_password = hash_password(password) 
    # TODO: Append the new user to the file
    # Format: username,hashed_password
    with open("users.txt", "a") as f: 
         f.write(f"{username},{hashed_password},{role}\n") 
    print(f"User '{username}' registered.")

    return True

#Step 8. Implement the User Existence Check
def user_exists(username):
 # TODO: Handle the case where the file doesn't exist yet
 # TODO: Read the file and check each line for the username
    if not os.path.exists(USER_DATA_FILE):
        return False

    try:
        with open(USER_DATA_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split only on the first comma (hash should not contain raw commas)
                user, _ = line.split(',', 1)
                if user == username:
                    return True
    except Exception:
        # If any error occurs reading the file, treat as no user found
        return False

    return False


# Implementing User Login
# Step 9. Implement the Login Function
def login_user(username, password):
 # TODO: Handle the case where no users are registered yet
    if not os.path.exists(USER_DATA_FILE):
        return False
 # TODO: Search for the username in the file
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            user, hash = line.split(',', 1) 
 # TODO: If username matches, verify the password
            if user == username:
                return verify_password(password, hash) 
 # TODO: If we reach here, the username was not found
    return False

# Building the Interactive Interface
# Step10. Implement Input Validation


def validate_username(username):
    """
    Checks a username against length, space, and character requirements.

    1. Minimum length of 3 characters, maximum of 15.
    2. Must not contain spaces.
    3. Must only contain letters (a-z, A-Z) and numbers (0-9).
    
    Returns:
        tuple: (bool, str) -> (is_valid, error_message)
    """

    # 1. Length Check
    if len(username) < 3 or len(username) > 15:
        return False, "Username must be between 3 and 15 characters long."

    # 2. Spaces Check
    if ' ' in username:
        return False, "Username cannot contain spaces."

    # 3. Valid Characters Check (only letters and numbers)
    # The regex pattern r'^[a-zA-Z0-9]+$' means:
    # ^ : start of string
    # [a-zA-Z0-9]+ : one or more letters (case-insensitive) or digits
    # $ : end of string
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        return False, "Username can only contain letters and numbers."
    
    # If all checks pass, the username is valid
    return True, "Username is valid!"

# --- Testing the Username Validator ---
usernames_to_test = [
    "go",             # Fails min length
    "SuperLongUsername12345", # Fails max length
    "User Name",      # Fails space check
    "User!",          # Fails invalid character check
    "User42",         # Success!
]

print("\n--- Testing Usernames ---")

for user in usernames_to_test:
    is_valid, error_msg = validate_username(user)
    
    print(f"\nChecking: '{user}'")
    
    if not is_valid:
        print(f"❌ Error: {error_msg}")
    else:
        print(f"✅ Success: {error_msg}")

def validate_password(password):
    """
    Checks a password against basic security requirements.
    
    Returns:
        tuple: (bool, str) -> (is_valid, error_message)
    """
    
    # Rule 1: Minimum Length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Rule 2: Must contain an uppercase letter
    # 'any()' checks if the condition is True for AT LEAST ONE character in the password
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    
    # Rule 3: Must contain a digit (number)
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."
        
    # If all checks pass, the password is valid
    return True, "Password is valid!"

# --- Putting it all together with the original snippet ---
passwords_to_test = [
    "short1",         # Fails length
    "Greateight",     # Fails number
    "tooweak1",       # Fails uppercase
    "StrongP@ss123"   # Success!
]

print("--- Testing Passwords ---")

# This loop simulates the flow your original snippet was in
for password in passwords_to_test:
    print(f"\nAttempting to validate: '{password}'")
    
    # This is your original code snippet!
    is_valid, error_msg = validate_password(password)
    
    if not is_valid:
        print(f"❌ Error: {error_msg}")
        print(">>> Loop would 'continue' here, prompting for a new password.")
        continue # Skips the rest of the loop block
        
    # This only runs if is_valid is True
    print(f"✅ Success: {error_msg}")
    print(">>> Loop would 'break' or proceed to the next step (e.g., storing the password).")

# Step 11. Implement the Main Menu
# the main program logic:

def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)
def main():
    """Mai
    n program loop."""
    print("\nWelcome to the Week 7 Authentication System!")
    
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
        
        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()
            
            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            
            password = input("Enter a password: ").strip()
 
            
            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            
            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
            
            role = input("Enter role (user/admin/analyst): ").strip().lower()
            if role not in ["user", "admin", "analyst"]:
                print("Error: Invalid role.Defaulting to 'user'.")
                role = "user"

            # Register the user
            register_user(username, password, role)
        
        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            
            # Attempt login
            if login_user(username, password):
                print(f"\nSuccess: Welcome {username}.")
                print("(In a real application, you would now access the data)")
                
                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")
            else:
                 # This block runs if login_user returns False (or a falsy value)
                 print("The username or password was incorrect. Please try again.")
        
        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
        
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")
if __name__ == "__main__":
    main()