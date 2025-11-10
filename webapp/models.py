from django.db import models
from django.core.validators import FileExtensionValidator
from   django.contrib.auth.models   import   User
from django.core.validators import RegexValidator
from   django.dispatch   import   receiver
from django.db.models.signals import pre_delete
import   os

#Mill_Owners_Profile
class   MillOwnersProfile(models.Model):
    owner_p =   models.ForeignKey(User,related_name="mills_owners_profiles", on_delete=models.CASCADE, default='')
    designation =  models.CharField(max_length=522)
    company =  models.CharField(max_length=522)
    customer_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^[A-Za-z0-9\-]+$', 'NTN must be alphanumeric (letters, numbers, or dashes).')]
    )


#Mills
class   Mills(models.Model):
    name =  models.CharField(max_length=255)
    units =  models.PositiveIntegerField(default=1)
    owner =   models.ForeignKey(User,related_name="mills_owners", on_delete=models.CASCADE, default='')



#Mills_Authorized_Point_of_Contact
class   Mills_Authorized_Point_of_Contact(models.Model):
    user = models.OneToOneField(User,related_name="mills_units_authority", on_delete=models.CASCADE, default='')
    contact = models.CharField(max_length=522)


#Mills_Senior_Point_of_Contact
class   Mills_Senior_Point_of_Contact(models.Model):
    user = models.ForeignKey(User,related_name="mills_units_senior", on_delete=models.CASCADE, default='')
    contact = models.CharField(max_length=522)

 
#Mills_Units
class   Mills_Units(models.Model):
    mill = models.ForeignKey(Mills,related_name="mills_units", on_delete=models.CASCADE, default='')
    address = models.CharField(max_length=522)
    lat  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lon  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    ntn = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        
    )
    gst =  models.PositiveIntegerField(null=True)
    spindles_installed =  models.PositiveIntegerField(null=True) 
    rotors_installed =  models.PositiveIntegerField(null=True)
    doubling_machines_installed =  models.PositiveIntegerField(null=True)
    mill_unit_inspectors = models.ForeignKey(User,related_name="mill_unit_inspectors", on_delete=models.CASCADE, null=True)
    authorized_p_contact = models.CharField(max_length=522,null=True)
    authorized_p_email = models.CharField(max_length=522,null=True)
    senior_p_contact = models.CharField(max_length=522,null=True)
    senior_p_email = models.CharField(max_length=522,null=True)
    unit_id  = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^[A-Za-z0-9\-]+$', 'NTN must be alphanumeric (letters, numbers, or dashes).')]
    )





#Inspection_Reports
class   Inspection_Reports(models.Model):
    inspector = models.ForeignKey(User,related_name="inspector_inspection_reports", on_delete=models.CASCADE, null=True, blank=True)
    mill = models.ForeignKey(Mills,related_name="mills_inspection_reports", on_delete=models.CASCADE, default='')
    mill_unit = models.ForeignKey(Mills_Units,related_name="mill_unit_inspection_reports", on_delete=models.CASCADE, default='')
    num_camera_installed = models.PositiveIntegerField(null=True)
    cameras_online =  models.PositiveIntegerField(null=True)
    cameras_offline =  models.PositiveIntegerField(null=True)
    cpu_online =  models.PositiveIntegerField(null=True)
    cpu_offline =  models.PositiveIntegerField(null=True)
    gpu_online =  models.PositiveIntegerField(null=True)
    gpu_offline =  models.PositiveIntegerField(null=True)
    tnt_software_online =  models.PositiveIntegerField(null=True)
    tnt_software_offline =  models.PositiveIntegerField(null=True)
    payment_recieved =  models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    created_at =  models.DateTimeField(auto_now_add = True,null=True)


     
#Payment Accounts
class  Paymentaccounts(models.Model):
    added_by_user = models.ForeignKey(User,related_name='payment_accounts_added_by_user', on_delete=models.CASCADE, null=True)
    iban_number = models.CharField(max_length=522,null=True)
    account_title = models.CharField(max_length=522,null=True) 
    bank_name = models.CharField(max_length=522,null=True)


#Payments  Records
class   PaymentsRecords(models.Model):
    mill = models.ForeignKey(Mills,related_name='payment_records_paid_by_mills', on_delete=models.CASCADE, null=True)
    unit = models.ForeignKey(Mills_Units,related_name='payment_records_paid_by_unit', on_delete=models.CASCADE, null=True)
    approved_by_inspector = models.ForeignKey(Mills_Authorized_Point_of_Contact,related_name='payment_records_approved_by_inspector', on_delete=models.CASCADE, null=True)
    paid_to_account =  models.ForeignKey(Paymentaccounts,related_name='payment_records_paid_to_account', on_delete=models.CASCADE, null=True)
    attachment = models.FileField(
        upload_to="static/payments_attachments/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])],
        null=True,
        blank=True
    )
    total_amount = models.DecimalField(max_digits=15,decimal_places=2,null=True)
    paid_amount = models.DecimalField(max_digits=15,decimal_places=2,null=True)
    unpaid_amount = models.DecimalField(max_digits=15,decimal_places=2,null=True)
    status_title  =   models.CharField(max_length=522,null=True)
    is_approved = models.BooleanField(default=False)
    payment_date =  models.DateTimeField(auto_now_add = True,null=True)



class   Master_Settings(models.Model): 
    contact = models.CharField(max_length=522,null=True)
    obsidian_logo = models.FileField(
        upload_to="static/master/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        null=True,
        blank=True
    )
    notf_1 = models.FileField(
        upload_to="static/master/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])],
        null=True,
        blank=True
    )
    notf_2 = models.FileField(
        upload_to="static/master/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])],
        null=True,
        blank=True
    )
    notf_3 = models.FileField(
        upload_to="static/master/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])],
        null=True,
        blank=True
    )



class ChatMessages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True,null=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f"{self.sender} ➜ {self.receiver}: {self.message}"
    


class  UsersLoginLogoutActivitiesLog(models.Model):
    user = models.ForeignKey(User,related_name="users_login_logout_activities_log", on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} {self.activity_type} @ {self.timestamp}"
    


class Invoice(models.Model):
    mill_unit_invoices = models.ForeignKey(Mills_Units, on_delete=models.CASCADE, related_name='mill_unit_invoices',null=True)
    invoice_no = models.CharField(max_length=50,validators=[RegexValidator(r'^[A-Za-z0-9\-]+$', 'NTN must be alphanumeric (letters, numbers, or dashes).')], unique=True)
    customer_name = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=50)
    bill_to = models.CharField(max_length=200)
    site_location = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(auto_now_add = True,null=True)
    remittance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='static/invoices/', blank=True, null=True)
    created_by = models.ForeignKey(User,related_name="invoices_created_by", on_delete=models.SET_NULL, null=True, blank=True)



@receiver(pre_delete, sender=Invoice)
def delete_pdf_file(sender, instance, **kwargs):
    """Automatically delete attached file when record is deleted."""
    if instance.pdf_file:
        # check if file exists on disk
        if os.path.isfile(instance.pdf_file.path):
            os.remove(instance.pdf_file.path)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items')
    serial_no = models.PositiveIntegerField(blank=True, null=True)
    item_name = models.CharField(max_length=200)
    pcs = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)



#Invoices Payments  Records
class   InvoicesPaymentsRecords(models.Model):
    invoice  =  models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='invoice_paid_payment_proof',null=True) 
    attachment = models.FileField(
        upload_to="static/invoices_payments_attachments/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])],
        null=True,
        blank=True
    )
    status_title  =   models.CharField(max_length=522,default="Pending")
    is_approved = models.BooleanField(default=False)
    paid_date =  models.DateTimeField(auto_now_add = True,null=True)



@receiver(pre_delete, sender=InvoicesPaymentsRecords)
def delete_attachment_file(sender, instance, **kwargs):
    """Automatically delete attached file when record is deleted."""
    if instance.attachment:
        # check if file exists on disk
        if os.path.isfile(instance.attachment.path):
            os.remove(instance.attachment.path)