import bcrypt


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hased password. Useing bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(str.encode(plain_text_password), hashed_password)
