import hashlib
import os

CREDS_FILE = '/home/who/whoOS/core/.creds'

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_user(username, password):
    with open(CREDS_FILE, 'w') as f:
        f.write(username + '\n' + hash_pass(password))

def check_creds(username, password):
    if not os.path.exists(CREDS_FILE):
        setup_user(username, password)
        return True
    with open(CREDS_FILE, 'r') as f:
        lines = f.read().splitlines()
    if len(lines) < 2:
        return False
    return lines[0] == username and lines[1] == hash_pass(password)

def user_exists():
    return os.path.exists(CREDS_FILE)
