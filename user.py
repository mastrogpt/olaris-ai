import os, sys, json
import bcrypt
from pathlib import Path
from prompt_toolkit import prompt

base = os.getenv("OPS_PWD")
user_file = f"{base}/packages/mastrogpt/login/users.json"

def hash_password(password: str) -> str:
    """
    Apply bcrypt hash algorithm to password.

    Args:
        password (str): Password to hash

    Returns:
        str: Hashed password
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def load():
    file = Path(user_file)
    if not file.exists():
        return {}
    try:
        return json.loads(file.read_text())
    except Exception as e:
        print(str(e))
        sys.exit(1)
        
def add_or_update(user, update=False):
    users = load()
    if not update and user in users:
        print("error: user already exist - try update")
        return False

    password = prompt("Enter your password: ", is_password=True)
    if len(password) < 6:
        print("please provide at least 6 characters")
        return False
        
    hashed_password = hash_password(password)  
    users[user] = hashed_password
    return save(users)
            
def delete(user):
    users = load()
    if not user in users:
        print(f"user {user} not found")
        return
    del users[user]
    return save(users)
    
def save(users):
    try:
        Path(user_file).write_text(json.dumps(users, indent=2))
        print(f"updated {user_file}")
        return True
    except Exception as e:
        print(str(e))
        return False

# arg check performed by docopts
def main(argv):
    op = argv[0]
    user = argv[1]
    if op == "add":
        add_or_update(user, False)
    elif op == "update":
        add_or_update(user, True)
    elif op == "delete":
       delete(user)
 
main(sys.argv[1:])
