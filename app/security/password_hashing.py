
from argon2 import PasswordHasher

hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return hasher.hash(password) 
        

def verify_password(password: str, hashed_password: str) -> bool:
    return hasher.verify(hashed_password, password)
    
