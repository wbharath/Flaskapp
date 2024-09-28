import secrets

key = secrets.token_hex(16)
print(f"Generated key: {key}")

# print(f"SECRET_KEY: {app.config['SECRET_KEY']}")