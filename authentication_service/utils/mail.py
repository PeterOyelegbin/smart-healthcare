from smtplib import SMTP, SMTPException, SMTPAuthenticationError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from .logger import logger

email_from_name = config('EMAIL_FROM_NAME')
email_from = config('EMAIL_FROM')
smtp_host = config('SMTP_HOST')
smtp_port = config('SMTP_PORT', cast=int)
smtp_username = config('SMTP_USERNAME')
smtp_password = config('SMTP_PASSWORD')

def send_password_reset_email(user: str, email: str, reset_token: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{email_from_name} <{email_from}>"
        msg["To"] = email
        msg["Subject"] = "Password Reset Request"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; font-size: 18px; line-height: 1.3; color: #333; padding: 0px 40px;">
                <p>Hello <strong>{user}</strong>,</p>
                <p>You have requested to reset your password for your SmartHealthCare account.</p>
                <p>Please click the button below to reset your password, it will expire in <strong>5 minutes</strong>:</p>
                <button style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; display: inline-block; font-size: 18px; border-radius: 5px; border: none;">
                    <a href="{config('FRONTEND_URL')}/reset-password?token={reset_token}" style="color: white; text-decoration: none;">Reset Password</a>
                </button>
                <p style="color: red;"><strong>If you did not request this, please ignore this email.</strong></p>
                <p>Best regards,<br>Support Team<br><strong>SmartHealthCare</strong></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        with SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(email_from, email, msg.as_string())
        logger.info(f"Password reset email sent successfully to {email}")
        return True
    except SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {str(e)}")
        return False
    except SMTPException as e:
        logger.error(f"SMTP error while sending email to {email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {email}: {str(e)}")
        return False
    