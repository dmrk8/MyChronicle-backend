from unittest.mock import patch, MagicMock
import pytest
from app.auth.password_handler import PasswordHandler


@pytest.fixture
def password_handler():
    return PasswordHandler()


def test_password_handler_init():
    handler = PasswordHandler()
    assert handler is not None
    assert handler.pwd_context is not None


def test_hash_password_returns_string(password_handler):
    hashed = password_handler.hash_password("SecurePassword@123")
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_hash_password_returns_different_hash_each_time(password_handler):
    plain_password = "SecurePassword@123"
    hash1 = password_handler.hash_password(plain_password)
    hash2 = password_handler.hash_password(plain_password)
    
    assert hash1 != hash2  # bcrypt includes random salt


def test_hash_password_empty_password_raises():
    handler = PasswordHandler()
    with pytest.raises(ValueError, match="Password cannot be empty"):
        handler.hash_password("")


def test_hash_password_none_password_raises():
    handler = PasswordHandler()
    with pytest.raises(ValueError, match="Password cannot be empty"):
        handler.hash_password(None)  # type: ignore


def test_verify_password_correct(password_handler):
    plain_password = "SecurePassword@123"
    hashed = password_handler.hash_password(plain_password)
    
    result = password_handler.verify_password(plain_password, hashed)
    assert result is True


def test_verify_password_incorrect(password_handler):
    plain_password = "SecurePassword@123"
    hashed = password_handler.hash_password(plain_password)
    
    result = password_handler.verify_password("WrongPassword@456", hashed)
    assert result is False


def test_verify_password_empty_plain_password(password_handler):
    hashed = password_handler.hash_password("SecurePassword@123")
    result = password_handler.verify_password("", hashed)
    assert result is False


def test_verify_password_empty_hashed_password(password_handler):
    result = password_handler.verify_password("SecurePassword@123", "")
    assert result is False


def test_verify_password_both_empty(password_handler):
    result = password_handler.verify_password("", "")
    assert result is False


def test_verify_password_complex_password(password_handler):
    complex_password = "MyP@ssw0rd!#$%^&*()"
    hashed = password_handler.hash_password(complex_password)
    
    result = password_handler.verify_password(complex_password, hashed)
    assert result is True


def test_verify_password_case_sensitive(password_handler):
    plain_password = "SecurePassword@123"
    hashed = password_handler.hash_password(plain_password)
    
    result = password_handler.verify_password("securepassword@123", hashed)
    assert result is False


def test_verify_password_long_password(password_handler):
    long_password = "A" * 100 + "@123"
    hashed = password_handler.hash_password(long_password)
    
    result = password_handler.verify_password(long_password, hashed)
    assert result is True


def test_hash_password_special_characters(password_handler):
    password_with_special = "P@ss!#dollarsign%carot^ampersand&asterisk*()"
    hashed = password_handler.hash_password(password_with_special)
    
    result = password_handler.verify_password(password_with_special, hashed)
    assert result is True


def test_hash_password_unicode_characters(password_handler):
    unicode_password = "Passw0rd!@#äöü"
    hashed = password_handler.hash_password(unicode_password)
    
    result = password_handler.verify_password(unicode_password, hashed)
    assert result is True


def test_verify_password_none_values(password_handler):
    result = password_handler.verify_password(None, "hash")
    assert result is False


def test_hash_password_single_character(password_handler):
    single_char = "A@1"
    hashed = password_handler.hash_password(single_char)
    
    result = password_handler.verify_password(single_char, hashed)
    assert result is True


def test_multiple_handlers_independent():
    handler1 = PasswordHandler()
    handler2 = PasswordHandler()
    
    password = "TestPassword@123"
    hashed1 = handler1.hash_password(password)
    hashed2 = handler2.hash_password(password)
    
    assert hashed1 != hashed2
    assert handler1.verify_password(password, hashed1) is True
    assert handler1.verify_password(password, hashed2) is True
