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

         
    
     



def truncate_float(value, decimal_places=2):
    # Convert the float to a string with enough precision
    value_str = f"{value:.{decimal_places + 1}f}"
    
    # Split the string on the decimal point
    integer_part, decimal_part = value_str.split('.')
    
    # Truncate the decimal part to the desired number of decimal places
    truncated_value_str = f"{integer_part}.{decimal_part[:decimal_places]}"
    
    # Convert the result back to a float
    return float(truncated_value_str)



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



def verify_email_smtp(email):
    domain = email.split('@')[-1]
    print("domain   ",domain)
    try:
        # Connect to the domain's mail server
        mx_records = dns.resolver.resolve(domain, 'MX')
        print("mx_records   ",mx_records)
        mx_record = str(mx_records[0].exchange)
        
        print("mx_record   ",mx_record)
        server = smtplib.SMTP(mx_record, 25)
        print("server   ",server)
        server.set_debuglevel(0)
        print("server.set_debuglevel(0)")
        server.helo()
        print("server.helo()")
        server.mail(settings.EMAIL_HOST_USER)
        print("server.mail(settings.EMAIL_HOST_USER)")
        code, message = server.rcpt(email) 

        print("smtp code  ",code,"   message  ", message)
        server.quit()
        print("server.quit()")

        
        
        # 250 is the success response code
        if code == 250:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error verifying email: {e}")
        return  4975




