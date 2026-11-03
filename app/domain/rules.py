"""Business rules shared by the API schemas and the service layer."""
import re

from app.domain.errors import WeakPasswordError

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\- ]{6,19}$")


def validate_password_strength(password: str) -> str:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise WeakPasswordError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise WeakPasswordError(f"Password must be at most {PASSWORD_MAX_LENGTH} characters long")
    if not re.search(r"[A-Z]", password):
        raise WeakPasswordError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise WeakPasswordError("Password must contain a lowercase letter")
    if not re.search(r"[0-9]", password):
        raise WeakPasswordError("Password must contain a digit")
    return password


def normalize_email(email: str) -> str:
    return email.strip().lower()


def normalize_name(value: str) -> str:
    return " ".join(value.split())
