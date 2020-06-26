from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
	('S','Stripe'),
	('C','Credit Card'),
	('P','Paypal'),
	('D', 'Debit Card')
)

class CheckoutForm(forms.Form):
	street_address = forms.CharField(widget = forms.TextInput(attrs = {
		'placeholder' : '1234 Main St',
		'id' : 'address'
		}))
	second_address = forms.CharField(required=False,widget = forms.TextInput(attrs={
		'placeholder' : 'Apartment or suite',
		'id' : 'address-2'
		}))
	country = CountryField(blank_label='(select country)').formfield()
	#widget = CountrySelectWidget(attrs ={'class' : 'custom-select d-block w-100'})
	zip_code = forms.CharField(widget = forms.TextInput(attrs = {
		'class' : 'form-control',
		'id' : 'zip'
		}))
	same_billing_address = forms.BooleanField(required = False,widget= forms.CheckboxInput())
	save_info = forms.BooleanField(required = False,widget = forms.CheckboxInput())
	# payment_option = forms.ChoiceField(required = False, choices = PAYMENT_CHOICES, widget=forms.RadioSelect())

class CheckoutFormShipping(forms.Form):
	street_address = forms.CharField(widget = forms.TextInput(attrs = {
		'placeholder' : '1234 Main St',
		'id' : 'address'
		}))
	second_address = forms.CharField(required=False,widget = forms.TextInput(attrs={
		'placeholder' : 'Apartment or suite',
		'id' : 'address-2'
		}))
	country = CountryField(blank_label='(select country)').formfield()
	#widget = CountrySelectWidget(attrs ={'class' : 'custom-select d-block w-100'})
	zip_code = forms.CharField(widget = forms.TextInput(attrs = {
		'class' : 'form-control',
		'id' : 'zip'
		}))
	# same_billing_address = forms.BooleanField(required = False,widget= forms.CheckboxInput())
	save_info = forms.BooleanField(required = False,widget = forms.CheckboxInput())
	payment_option = forms.ChoiceField(required = False, choices = PAYMENT_CHOICES, widget=forms.RadioSelect())


class CouponForm(forms.Form):
	code = forms.CharField(widget = forms.TextInput(attrs = {
		'class' : 'form-control',
		'placeholder' : 'Promo code',
		'aria-label' : "Recipient's username",
		'aria-describedby' : "basic-addon2"
		}))	

class RequestRefundForm(forms.Form):
	ref_code = forms.CharField()
	message = forms.CharField(widget = forms.Textarea(attrs = {
		'rows' : 4
		}))
	email = forms.EmailField()