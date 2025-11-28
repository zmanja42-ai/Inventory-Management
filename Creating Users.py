import bcrypt

password = "Freedom123"  # ← your chosen password
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed.decode())
