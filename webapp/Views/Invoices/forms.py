from django import forms
from django.forms import inlineformset_factory
from  webapp.models import Invoice, InvoiceItem , HardwareInvoiceItems   ,  SoftwareInvoiceItems

class InvoiceForm(forms.ModelForm):
    # date = forms.DateField(
    #     widget=forms.DateInput(attrs={'type': 'date'}),
    #     input_formats=['%Y-%m-%d'],
    # )

    class Meta:
        model = Invoice
        fields = ['invoice_no', 'customer_name', 'customer_id', 'bill_to', 'site_location',  'remittance_amount']
        exclude = ('remittance_amount',)

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        exclude = ('invoice',)

InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm,
    extra=1, can_delete=True
)


class  HardwareInvoiceItemsForm(forms.ModelForm):
    class Meta:
        model = HardwareInvoiceItems
        exclude = ('invoice',)


class   SoftwareInvoiceItemsForm(forms.ModelForm):
    class Meta:
        model = SoftwareInvoiceItems
        exclude = ('invoice',)

SoftwareFormSet = inlineformset_factory(Invoice, SoftwareInvoiceItems, form=SoftwareInvoiceItemsForm, extra=1, can_delete=True)
HardwareFormSet = inlineformset_factory(Invoice, HardwareInvoiceItems, form=HardwareInvoiceItemsForm, extra=1, can_delete=True)
