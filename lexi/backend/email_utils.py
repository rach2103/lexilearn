import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import os

def _send_email_sync(smtp_server, smtp_port, smtp_username, smtp_password, msg):
    """Synchronous email sending function"""
    with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

async def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email asynchronously"""
    try:
        # Email configuration from environment
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', 'yourusername@gmail.com')
        smtp_password = os.getenv('SMTP_PASSWORD', 'your-pwd')
        
        # Create reset URL
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        # Create email content
        subject = "Reset Your LexiLearn Password"
        
        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password for your LexiLearn account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="background-color: #4f46e5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The LexiLearn Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        You requested to reset your password for your LexiLearn account.
        
        Click this link to reset your password: {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The LexiLearn Team
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username  # Use SMTP_USERNAME to prevent rejection
        msg['To'] = email
        
        # Attach parts
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email in thread pool to avoid blocking
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, 
            _send_email_sync, 
            smtp_server, smtp_port, smtp_username, smtp_password, msg
        )
        
        print(f"[SUCCESS] Password reset email sent to: {email}")
        
    except Exception as e:
        print(f"[ERROR] Failed to send password reset email: {str(e)}")
        raise e