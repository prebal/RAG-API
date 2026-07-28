import argon2
from argon2 import PasswordHasher
from typing import Union

hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return hasher.hash(password) 
        

def verify_password(password: str, hashed_password: str) -> bool:
    return hasher.verify(hashed_password, password)
    
