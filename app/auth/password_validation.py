def validate_password_strength(value: str) -> str:
    if not any(c.islower() for c in value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one digit")
    if not any(not c.isalnum() for c in value):
        raise ValueError("Password must contain at least one symbol")
    return value
