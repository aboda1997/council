import bcrypt


def hash_password(password: str) -> str:
    """
    Hashs the provided password using bcrypt
    (The salt is saved into the hash itself)
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))


def verify_password(plain_password: str, hashed_password: str) -> str:
    """
    Verify that the plain password is the same as the one hashed using bcrypt
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), hashed_password.encode('utf-8')
    )
