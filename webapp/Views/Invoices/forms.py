from django import forms
from django.forms import inlineformset_factory
from  webapp.models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )
    
    class Meta:
        model = Invoice
        fields = ['invoice_no', 'customer_name', 'customer_id', 'bill_to', 'site_location', 'date', 'remittance_amount']

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        exclude = ('invoice',)

InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm,
    extra=1, can_delete=True
)
