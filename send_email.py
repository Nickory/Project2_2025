import smtplib
from email.message import EmailMessage

# QQ Mail Configuration
from_email_addr = "3119349688@qq.com"      # Sender's QQ email
from_email_pass = "okhhgidjogtndfid"       # QQ email authorization code

to_email_addr = "2563373919@qq.com"        # Recipient's email

try:
    # Create email object
    msg = EmailMessage()
    msg.set_content("Hello from Raspberry Pi")
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    msg['Subject'] = 'TEST EMAIL'

    # Connect to QQ Mail SMTP server (SSL encrypted)
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        # Debug mode (show SMTP protocol interaction)
        server.set_debuglevel(1)
        
        # Log in using authorization code
        server.login(from_email_addr, from_email_pass)
        
        # Send the email
        server.send_message(msg)
        print('Email successfully sent to QQ Mail queue')

except smtplib.SMTPAuthenticationError:
    print("SMTP authentication error")
except smtplib.SMTPException as e:
    print(f"SMTP error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
