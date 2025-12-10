import pytest
from models.auth.validations import validate_login_form, validate_activation_passwords


class TestValidateLoginForm:
    def test_valid_input(self):
        # Should return None when both username and password are provided.
        assert validate_login_form("mary", "password123") is None

    def test_missing_username(self):
        #  Should raise ValueError when the username is empty.
        with pytest.raises(
            ValueError, match="Please enter both username and password."
        ):
            validate_login_form("", "password123")

    def test_missing_password(self):
        # Should raise ValueError when the password is empty.
        with pytest.raises(
            ValueError, match="Please enter both username and password."
        ):
            validate_login_form("juliana", "")

    def test_missing_both(self):
        # Should raise ValueError when both username and password are empty.
        with pytest.raises(
            ValueError, match="Please enter both username and password."
        ):
            validate_login_form("", "")


class TestValidateActivationPasswords:
    def test_valid_matching_passwords(self):
        #  Should return None when passwords match and meet the required complexity.
        valid = "StrongP@ssw0rd123!"
        assert validate_activation_passwords(valid, valid) is None

    def test_missing_both_passwords(self):
        #  Should raise ValueError when both password fields are empty.
        with pytest.raises(ValueError, match="Please fill in all password fields."):
            validate_activation_passwords("", "")

    def test_missing_one_password(self):
        # Should raise ValueError when one of the password fields is missing.
        with pytest.raises(ValueError):
            validate_activation_passwords("StrongP@ssw0rd!", "")

    def test_passwords_do_not_match(self):
        # Should raise ValueError when new password and confirm password do not match.
        with pytest.raises(ValueError, match="Passwords do not match."):
            validate_activation_passwords("StrongP@ssw0rd!", "DifferentP@ssw0rd!")

    def test_password_does_not_meet_pattern_requirements(self):
        # Should raise ValueError when the password does not satisfy complexity rules.
        # invalid: missing special characters and uppercase letter
        invalid = "weakpassword123"
        with pytest.raises(
            ValueError,
            match="Password must be 8-64 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
        ):
            validate_activation_passwords(invalid, invalid)
