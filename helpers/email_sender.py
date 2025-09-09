import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_PASS, SMTP_HOST, SMTP_PORT, SMTP_USER, BASE_DOMAIN
from helpers.logger import AppLogger

logger = AppLogger()


class EmailSender:
    def __init__(self):
        """Initialize SMTP server connection"""
        try:
            self.server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            self.server.starttls()
            self.server.login(user=SMTP_USER, password=SMTP_PASS)
            logger.log_info("📧 SMTP server connected successfully.")
        except Exception as e:
            logger.log_exception(f"🚨 SMTP connection failed: {e}")
            self.server = None

    def load_template(self, template_name, context):
        """Loads an HTML email template and fills placeholders with actual data."""
        template_path = os.path.join("email_templates", f"{template_name}.html")

        try:
            with open(template_path, "r", encoding="utf-8") as file:
                template = file.read()

            for key, value in context.items():
                template = template.replace(f"{{{{{key}}}}}", value)

            return template
        except FileNotFoundError:
            logger.log_error(f"❌ Template '{template_name}.html' not found.")
            return None

    def send_email(self, to_email, subject, template_name, context):
        """Send an email with an HTML template."""
        if not self.server:
            logger.log_error("🚨 Email sending failed: SMTP server not initialized.")
            return False

        html_content = self.load_template(template_name, context)
        if not html_content:
            return False

        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))

        try:
            self.server.sendmail(SMTP_USER, to_email, msg.as_string())
            logger.log_info(f"✅ {subject} email sent to {to_email}")
            return True
        except Exception as e:
            logger.log_exception(
                f"❌ {subject} failed to send email to {to_email}: {e}"
            )
            return False

    def account_confirmation(self, to_email: str, verification_token: str):
        """
        Sends an account confirmation email.

        Parameters:
            to_email (str): The recipient's email address.
            verification_token (str): A JWT token for email verification.

        Returns:
            None
        """
        return self.send_email(
            to_email=to_email,
            subject="Confirm Your Account",
            template_name="account_confirmation",
            context={
                "verification_link": f"{BASE_DOMAIN}/auth/verify?token={verification_token}"
            },
        )

    def forgot_password(self, to_email: str, password_reset_token: str):
        """
        Sends an forgot password email.

        Parameters:
            to_email (str): The recipient's email address.
            password_reset_token (str): A JWT token for email verification.

        Returns:
            None
        """
        return self.send_email(
            to_email=to_email,
            subject="Forgot Your Password",
            template_name="forgot_password",
            context={
                "verification_link": f"{BASE_DOMAIN}/auth/reset-password?token={password_reset_token}"
            },
        )

    def close_connection(self):
        """Close SMTP connection"""
        if self.server:
            self.server.quit()
            logger.log_info("🔌 SMTP connection closed.")


if __name__ == "__main__":
    email_sender = EmailSender()

    success = email_sender.send_email(
        to_email=SMTP_USER,
        subject="Test email",
        template_name="account_confirmation",
        context={"verification_link": "https://yourwebsite.com/verify?token=abc123"},
    )

    email_sender.close_connection()
