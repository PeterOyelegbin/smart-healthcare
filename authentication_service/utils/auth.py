from sqlalchemy.orm import Session
from database.models import User
from database.db_config import get_db, redis_client
from fastapi import Depends, security, HTTPException, status
from .security import verify_company, hash_password, verify_password, create_token_pair, decode_token, get_expires_at
from .logger import logger
from smtplib import SMTP, SMTPException, SMTPAuthenticationError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

oauth2_scheme = security.HTTPBearer()

def register_user(db: Session, user_data):
    verification = verify_company(user_data)
    print(verification.get("success"))
    if not verification.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company verification failed, check your details and try again.")
    hashed_pw = hash_password(user_data.password)
    user = User(organisation=user_data.business_name, email=user_data.email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password!")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password!")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive, contact support!")
    token = create_token_pair({"sub": user.email})
    return token

def blacklist_token(token: str) -> bool:
    try:
        expires_in = get_expires_at(token)
        key = f"blacklist:{token}"
        redis_client.setex(key, expires_in, "revoked")
        return True
    except Exception:
        return False

def is_token_blacklisted(token: str) -> bool:
    key = f"blacklist:{token}"
    return redis_client.exists(key) > 0

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if is_token_blacklisted(token.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, login again to continue.")
    user_email = decode_token(token.credentials).get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    return user
    
def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def password_update(db: Session, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password):
        return None
    hashed_pw = hash_password(new_password)
    user.password = hashed_pw
    db.commit()
    db.refresh(user)
    return user

def send_email(user: str, email: str, reset_token: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{config('EMAIL_FROM_NAME')} <{config('EMAIL_FROM')}>"
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
        with SMTP(config('SMTP_HOST'), config('SMTP_PORT', cast=int)) as server:
            server.starttls()
            server.login(config('SMTP_USERNAME'), config('SMTP_PASSWORD'))
            server.sendmail(config('EMAIL_FROM'), email, msg.as_string())
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
    
def password_reset(db: Session, user: User, new_password: str):
    """Reset user password"""
    hashed_pw = hash_password(new_password)
    user.password = hashed_pw
    db.commit()
    db.refresh(user)
    logger.info(f"Password reset for user: {user.email}")
    return user
