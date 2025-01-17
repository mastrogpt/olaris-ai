import os, sys, json
from pathlib import Path
import hashlib

from prompt_toolkit import prompt

base = os.getenv("OPS_PWD")
user_file = f"{base}/packages/mastrogpt/login/users.json"
users = {}

def load():
    global users
    try:
        users = json.loads(Path(user_file).read_text())
    except Exception as e:
        print(str(e))
        sys.exit(1)
        
def add(user):
    password = prompt("Enter your password: ", is_password=True)
    if len(password) < 6:
        print("please at least 6 characters")
        
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)

    hashed_password = hash_object.hexdigest()


def save():
    try:
        Path(user_file).write_te
        users = json.loads(Path(f"{base}/{user_file}").read_text())
    except Exception as e:
        print(str(e))
        sys.exit(1)

# arg check performed by docopts
def main(argv):
    op = argv[0]
    user = argv[1]
    if op == "add":
        print("add")
    elif op == "delete":
        print("delete")
    elif op == "update":
        print("update")

main(sys.argv[1:])
