import hashlib, hmac, os

def hash_password(password):
    salt=os.urandom(16); digest=hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180000)
    return salt.hex()+":"+digest.hex()

def verify_password(password, stored):
    try:
        salt,digest=stored.split(":",1); actual=hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 180000)
        return hmac.compare_digest(actual.hex(), digest)
    except Exception: return False
