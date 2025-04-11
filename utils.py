import random
import string

def generate_unique_key(existing_keys, length=8):
    while True:
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if key not in existing_keys:
            return key
