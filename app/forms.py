from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
	('C','Credit Card'),
	('P','Paypal'),
	('D', 'Debit Card')
)

class CheckoutForm(forms.Form):
	street_address = forms.CharField(widget = forms.TextInput(attrs = {
		'placeholder' : '1234 Main St'
		}))
	second_address = forms.CharField(required=False,widget = forms.TextInput(attrs={
		'placeholder' : 'Apartment or suite'
		}))
	country = CountryField(blank_label='(select country)').formfield()
	zip_code = forms.CharField(widget = forms.TextInput(attrs = {
		'class' : 'form-control',
		'id' : 'zip'
		}))
	same_billing_address = forms.BooleanField(widget= forms.CheckboxInput())
	save_info = forms.BooleanField(widget = forms.CheckboxInput())
	payment_option = forms.ChoiceField(choices = PAYMENT_CHOICES, widget=forms.RadioSelect())