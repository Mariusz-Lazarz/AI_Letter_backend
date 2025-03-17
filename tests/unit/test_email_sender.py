import pytest
import os
from unittest.mock import patch
from helpers.email_sender import EmailSender
from config import BASE_DOMAIN

REAL_TEMPLATES_DIR = "email_templates"


@pytest.fixture
def email_sender():
    """Fixture to create a fresh EmailSender instance."""
    return EmailSender()

@pytest.mark.parametrize(
    "template_name, context, expected_found",
    [
        ("account_confirmation", {"verification_link": "https://example.com"}, True),
        ("missing_template", {}, False), 
    ]
)
def test_load_template(email_sender, template_name, context, expected_found):
    """Test email template loading with real templates."""
    template_path = os.path.join(REAL_TEMPLATES_DIR, f"{template_name}.html")

    if expected_found:
        assert os.path.exists(template_path), f"Template '{template_name}.html' is missing in {REAL_TEMPLATES_DIR}"

    with patch.object(EmailSender, "load_template", wraps=email_sender.load_template) as mock_method:
        result = email_sender.load_template(template_name, context)

    if expected_found:
        assert result is not None  
        assert context["verification_link"] in result  
    else:
        assert result is None  

@pytest.mark.parametrize(
    "to_email, token, url_suffix, method_name, subject, template_name",
    [
        ("user@example.com", "fake_token_123", "/auth/verify?token=", "account_confirmation", "Confirm Your Account", "account_confirmation"),
        ("user@example.com", "fake_token_123", "/auth/reset-password?token=", "forgot_password", "Forgot Your Password", "forgot_password"),
    ]
)
def test_email_sending(email_sender, to_email, token, url_suffix, method_name, subject, template_name):
    """Test email sending for various scenarios."""
    with patch.object(email_sender, "send_email") as mock_send_email:
        getattr(email_sender, method_name)(to_email, token)
        mock_send_email.assert_called_once_with(
            to_email=to_email,
            subject=subject,
            template_name=template_name,
            context={"verification_link": f"{BASE_DOMAIN}{url_suffix}{token}"}
        )


@pytest.fixture
def email_sender():
    """Fixture to create a fresh EmailSender instance with mocked SMTP."""
    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.return_value.login.return_value = True
        yield EmailSender()

@pytest.mark.parametrize(
    "to_email, subject, template_name, context, smtp_raises, expected_result",
    [
        ("user@example.com", "Test Subject", "account_confirmation", {"verification_link": "https://example.com"}, False, True),
        ("user@example.com", "Test Subject", "missing_template", {}, False, False),  
        ("user@example.com", "Test Subject", "account_confirmation", {"verification_link": "https://example.com"}, True, False), 
    ]
)
def test_send_email(email_sender, to_email, subject, template_name, context, smtp_raises, expected_result):
    """Test sending emails with different conditions."""
    with patch.object(email_sender, "load_template", return_value="<html>Email Content</html>" if template_name != "missing_template" else None):
        with patch.object(email_sender.server, "sendmail") as mock_sendmail:
            if smtp_raises:
                mock_sendmail.side_effect = Exception("SMTP Error")

            result = email_sender.send_email(to_email, subject, template_name, context)
            assert result == expected_result 