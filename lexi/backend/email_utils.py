import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging
from datetime import datetime, timedelta
import secrets
from typing import Optional

logger = logging.getLogger(__name__)

# Token storage (in production, use Redis/database)
reset_tokens = {}

def generate_reset_token(email: str) -> str:
    """Generate secure password reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset_tokens[token] = {
        'email': email,
        'expires_at': expires_at,
        'used': False
    }
    
    return token

def verify_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email if valid"""
    token_data = reset_tokens.get(token)
    
    if not token_data or token_data['used'] or datetime.utcnow() > token_data['expires_at']:
        return None
    
    return token_data['email']

def use_reset_token(token: str) -> bool:
    """Mark reset token as used"""
    if token in reset_tokens:
        reset_tokens[token]['used'] = True
        return True
    return False

async def send_password_reset_email(email: str, reset_token: str = None):
    """Send password reset email to user"""
    if not reset_token:
        reset_token = generate_reset_token(email)
    
    # For development - log the reset link to console
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    print(f"\n=== PASSWORD RESET EMAIL ===")
    print(f"To: {email}")
    print(f"Reset Link: {reset_link}")
    print(f"Token expires in 1 hour")
    print(f"===========================\n")
    
    if not all([settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.FROM_EMAIL]):
        print("WARNING: Email configuration not complete. Reset link logged above for development.")
        return True  # Return True for development
    
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "LexiLearn - Password Reset Request"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 LexiLearn</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>Hello!</p>
                    <p>We received a request to reset your password for your LexiLearn account.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="http://localhost:3000/reset-password?token={reset_token}" class="button">Reset Password</a>
                    <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    <p>Best regards,<br>The LexiLearn Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""Hello!

You have requested to reset your password for your LexiLearn account.

Please visit this link to reset your password:
http://localhost:3000/reset-password?token={reset_token}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
The LexiLearn Team"""
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output
            server.starttls(context=context)
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, email, msg.as_string())
        
        print(f"SUCCESS: Email sent to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {str(e)}")
        print("Check your email credentials in .env file")
        return True  # Return True for development
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {str(e)}")
        return True  # Return True for development
    except Exception as e:
        print(f"General Error: {str(e)}")
        return True  # Return True for development