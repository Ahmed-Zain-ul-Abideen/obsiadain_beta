from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


import smtplib
import dns.resolver



from django.utils import timezone

def invalidate_user_tokens(user):
    """
    Invalidates all existing tokens for a given user by updating 
    their last_login timestamp.
    """
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

def verify_email_smtp(email):
    domain = email.split('@')[-1]
    try:
        # Get MX record
        mx_record = str(dns.resolver.resolve(domain, 'MX')[0].exchange)
        
        # Connect to mail server
        server = smtplib.SMTP(mx_record)
        server.helo()
        server.mail('check@example.com')
        code, message = server.rcpt(email)
        server.quit()

        if code == 250:
            return True  # Email exists
        else:
            return False
    except Exception as e:
        print("Verification error:", e)
        return 4975

 

# def verify_email_smtp(email):
#     try:
#         domain = email.split('@')[1]
#         print("domain  ",domain)

#         # resolve MX
#         mx_records = dns.resolver.resolve(domain, 'MX')
#         mx_record = str(mx_records[0].exchange)

#         # try secure ports
#         stat = False
#         for port in [25, 465, 587]:
#             try:
#                 if port == 465:
#                     server = smtplib.SMTP_SSL(mx_record, port, timeout=8)
#                 else:
#                     server = smtplib.SMTP(mx_record, port, timeout=8)
#                     server.starttls()
                
#                 server.helo()
#                 server.mail("test@example.com")
#                 code, _ = server.rcpt(email)
#                 server.quit()

#                 print("code ",code, "   port  ",port)

#                 if  code == 250:
#                     stat = True
#             except  Exception   as   e:
#                 print("stat ",stat)
#                 if  stat:
#                     pass
#                 else:
#                     stat  =  4975
#                 print("port   wise  e ",port ,"  ",e)
#                 continue

#         return  stat

#     except Exception as e:
#         print(f"Error verifying email: {e}")
#         return  4975
         
    
     



def truncate_float(value, decimal_places=2):
    # Convert the float to a string with enough precision
    value_str = f"{value:.{decimal_places + 1}f}"
    
    # Split the string on the decimal point
    integer_part, decimal_part = value_str.split('.')
    
    # Truncate the decimal part to the desired number of decimal places
    truncated_value_str = f"{integer_part}.{decimal_part[:decimal_places]}"
    
    # Convert the result back to a float
    return float(truncated_value_str)

# def verify_email_smtp(email):
#     domain = email.split('@')[-1]
#     try:
#         # Connect to the domain's mail server
#         mx_records = dns.resolver.resolve(domain, 'MX')
#         mx_record = str(mx_records[0].exchange)
        
#         server = smtplib.SMTP(mx_record)
#         server.set_debuglevel(0)
#         server.helo()
#         server.mail(settings.EMAIL_HOST_USER)
#         code, message = server.rcpt(email)
#         server.quit()

#         print("smtp code",code)
        
#         # 250 is the success response code
#         if code == 250:
#             return True
#         else:
#             return False
#     except Exception as e:
#         print(f"Error verifying email: {e}")
#         return  4975


def send_html_email(subject, to_email, context,template_path):
    # Create the HTML content
    html_content = render_to_string(template_path, context)
    text_content = strip_tags(html_content)  # This is optional, but recommended for email clients that do not support HTML
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # plain text
        from_email= settings.EMAIL_HOST_USER,
        to=[to_email]
    )
    
    # Attach the HTML content
    email.attach_alternative(html_content, "text/html")
    
    # Send the email
    email.send(fail_silently=True)



 
from django.core.mail import get_connection

def verify_sender_recipient_status(from_email, to_email_list):
    """
    Establishes an SMTP connection using Django settings, authenticates, 
    and verifies sender/recipient addresses using MAIL FROM/RCPT TO commands 
    without sending the actual email data.
    """
    connection = None
    smtp_server = None
    results = {}

    try:
        # 1. Get the Django connection object which manages settings abstraction
        connection = get_connection(fail_silently=False)
        
        # 2. Open the connection and authenticate (Handshake & AUTH LOGIN)
        # This populates connection.connection with the raw smtplib.SMTP object
        connection.open()
        
        # Access the raw smtplib object to manually issue commands
        smtp_server = connection.connection 

        print(f"Connection successful. Authenticated as {settings.EMAIL_HOST_USER}")

        # 3. Verify the Sender address (MAIL FROM)
        # The smtplib send_message function internally uses the below commands. 
        # We manually use mail() here to check status without DATA.
        try:
            # .mail() issues the 'MAIL FROM:<address>' command
            code, resp = smtp_server.mail(from_email)
            if code == 250:
                results['sender_status'] = f"Sender {from_email} accepted (Code 250 OK)"
            else:
                results['sender_status'] = f"Sender {from_email} rejected (Code {code}: {resp.decode()})"
        except smtplib.SMTPRecipientsRefused as e:
            results['sender_status'] = f"Sender {from_email} globally refused. Error: {e.recipients}"
            
        # 4. Verify Recipients (RCPT TO)
        results['recipients'] = {}
        for recipient in to_email_list:
            try:
                # .rcpt() issues the 'RCPT TO:<address>' command
                code, resp = smtp_server.rcpt(recipient)
                if code == 250 or code == 251: # 251 means user not local, but will forward
                    results['recipients'][recipient] = f"Accepted (Code {code})"
                else:
                    results['recipients'][recipient] = f"Rejected (Code {code}: {resp.decode()})"
            except smtplib.SMTPRecipientsRefused as e:
                # This exception is generally not raised by .rcpt(), manual code check works better
                results['recipients'][recipient] = f"Globally refused (Error: {e.recipients})"

        # CRITICAL: We stop here before calling the DATA command to send email content.

    except smtplib.SMTPAuthenticationError:
        results['error'] = "Authentication Error: Check credentials."

    except Exception as e:
        results['error'] = f"A connection error occurred: {e}"

    finally:
        # 5. Quit the connection gracefully
        if smtp_server:
            smtp_server.quit()
            print("Connection closed.")

    return results



def verify_email_via_smtp(sender_email, recipient_email, smtp_server="smtp.gmail.com", smtp_port=587, username="ijazhooria321@gmail.com", password="wjiqugvkakcddzog"):
    """
    Verify if recipient email exists by performing SMTP handshake
    without sending the actual message.

    Args:
        sender_email (str): The sender's email address.
        recipient_email (str): The recipient's email address to verify.
        smtp_server (str): SMTP server to connect to.
        smtp_port (int): SMTP port (default 587 for STARTTLS).
        username (str): Optional SMTP username (if authentication required).
        password (str): Optional SMTP password.

    Returns:
        dict: {'success': bool, 'message': str}
    """

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()

        # Authenticate if needed
        if username and password:
            server.login(username, password)

        # Perform SMTP handshake steps manually
        code, response = server.mail(sender_email)
        if code != 250:
            return {'success': False, 'message': f"MAIL FROM rejected: {response.decode()}"}

        code, response = server.rcpt(recipient_email)
        if code == 250:
            result = {'success': True, 'message': f"{recipient_email} is valid and accepted by the server."}
        elif code == 550:
            result = {'success': False, 'message': f"{recipient_email} was rejected (does not exist or blocked)."}
        else:
            result = {'success': False, 'message': f"Unknown RCPT response {code}: {response.decode()}"}

        # Close the connection before DATA command
        server.quit()
        return result

    except smtplib.SMTPConnectError as e:
        return {'success': False, 'message': f"Connection error: {e}"}
    except smtplib.SMTPServerDisconnected:
        return {'success': False, 'message': "Server unexpectedly disconnected."}
    except Exception as e:
        return {'success': False, 'message': f"Error: {str(e)}"}

