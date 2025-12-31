from auth import get_password_hash, verify_password

try:
    print("Testing password hash...")
    pwd = "password123"
    print(f"Password: {pwd} (len: {len(pwd)})")
    
    hashed = get_password_hash(pwd)
    print(f"Hash success: {hashed}")
    
    verified = verify_password(pwd, hashed)
    print(f"Verify success: {verified}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting long password...")
try:
    long_pwd = "x" * 100
    hashed = get_password_hash(long_pwd)
    print("Long password hash success")
except Exception as e:
    print(f"Long password ERROR: {e}")
