from app.security import encode_demo_token
print("DEVELOPMENT ONLY — never use this issuer in production.")
print(encode_demo_token())
