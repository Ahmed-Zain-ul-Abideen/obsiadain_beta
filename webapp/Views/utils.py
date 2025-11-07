from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


import smtplib
import dns.resolver

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
    email.send()
