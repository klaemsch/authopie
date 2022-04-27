from passlib.context import CryptContext

ctx = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


def verify_password(plain_password, hashed_password):
    return ctx.verify(plain_password, hashed_password)


def get_password_hash(password):
    return ctx.hash(password)
