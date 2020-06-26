from django.conf import settings
from django.shortcuts import render
from .models import Item,Order,OrderItem
from django.views.generic import ListView,DetailView,View
from django.shortcuts import get_object_or_404,redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from app.forms import CheckoutForm, CouponForm,RequestRefundForm, CheckoutFormShipping
from .models import Address,Payment,Coupon,Refund
# Create your views here.

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

import string
import random

def reference_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))

def home(request):
	context = {
		'items' : Item.objects.all()		
	}
	return render(request,'home-page.html',context);

def item(request):

	context = {
		'items' : Item.objects.all()		
	}
	return render(request,'item-list.html',context)


class HomeView(ListView):
	model = Item
	paginate_by = 10
	template_name = 'home-page.html'

class OrderSummary(LoginRequiredMixin,View):
	def get(self,*args,**kwargs):
		try:
			order = Order.objects.get(user=self.request.user,ordered=False)
			context = {
				'object' : order
			}
			return render(self.request,'account/order_summary.html',context)
		except ObjectDoesNotExist:
			messages.error(self.request,"You do not have an active order")
			return redirect("/") 
	
class ItemDetailView(DetailView):
	model = Item
	template_name = 'product-page.html'

@login_required
def add_to_card_summary(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_item,created = OrderItem.objects.get_or_create(item=item,user = request.user, ordered=False)
	order_qs = Order.objects.filter(user=request.user,ordered=False)

	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request,"This item updated")
			return redirect("app:order-summary")
		else:
			messages.info(request,"This item added to your card")
			order.items.add(order_item)
			return redirect("app:order-summary")
	else:
		messages.info(request,"Order created")
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user,ordered_date = ordered_date)
		order.items.add(order_item)

		return redirect("app:product")

@login_required
def add_to_card(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_item,created = OrderItem.objects.get_or_create(item=item,user = request.user, ordered=False)
	order_qs = Order.objects.filter(user=request.user,ordered=False)

	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request,"This item updated")
			return redirect("app:product",slug=slug)
		else:
			messages.info(request,"This item added to your card")
			order.items.add(order_item)
			return redirect("app:product",slug=slug)
	else:
		messages.info(request,"Order created")
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user,ordered_date = ordered_date)
		order.items.add(order_item)

		return redirect("app:product",slug=slug)
		

@login_required
def remove_from_card(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_qs = Order.objects.filter(user=request.user,ordered=False)

	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug = item.slug).exists():
			messages.info(request,"Order removed successfully")
			order_item = OrderItem.objects.filter(user=request.user,item=item,ordered=False)[0]
			# order_item.quantity = 0				
			order.items.remove(order_item)
			# order.save()
			# order_item.save()
		else:
			messages.info(request,"This item was not in your card")
			return redirect("app:product",slug=slug)
	else:
		messages.info(request,"Order does not exist")
		return redirect("app:product",slug=slug)

	return redirect("app:product",slug=slug)

@login_required
def remove_single_item_from_card(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_qs = Order.objects.filter(user=request.user,ordered=False)

	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug = item.slug).exists():
			messages.info(request,"Order removed successfully")
			order_item = OrderItem.objects.filter(user=request.user,item=item,ordered=False)[0]	
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			# order.save()
			
			return redirect("app:order-summary")
		else:
			messages.info(request,"This item was not in your card")
			return redirect("app:order-summary",slug=slug)
	else:
		messages.info(request,"Order does not exist")
		return redirect("app:order-summary",slug=slug)

	return redirect("app:order-summary",slug=slug)

@login_required
def remove_all_item_from_card(request,slug):
	item = get_object_or_404(Item,slug=slug)
	order_qs = Order.objects.filter(user=request.user,ordered=False)

	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug = item.slug).exists():
			messages.info(request,"Order removed successfully")
			order_item = OrderItem.objects.filter(user=request.user,item=item,ordered=False)[0]	
			
			order.items.remove(order_item)
			# order_item.quantity = 0
			# order_item.save()
			return redirect("app:order-summary")
		else:
			messages.info(request,"This item was not in your card")
			return redirect("app:order-summary",slug=slug)
	else:
		messages.info(request,"Order does not exist")
		return redirect("app:order-summary",slug=slug)

	return redirect("app:order-summary",slug=slug)

class Checkout(View):
	
	def get(self,*args,**kwargs):
		form = CheckoutForm()
		form2 = CheckoutFormShipping()
		try:
			order = Order.objects.get(user = self.request.user,ordered=False)
			forms = {
				'form' : form,
				'form2' : form2,
				'order' : order,
				'couponform' : CouponForm(),

			}
			return render(self.request,"checkout-page.html",forms)
		except ObjectDoesNotExist:
			messages.info(self.request,"Order does not exist")
			return redirect("app:checkout")

		

	def post(self,*args,**kwargs):
		form = CheckoutForm(self.request.POST or None)
		form2 = CheckoutFormShipping(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user,ordered=False)
			
			print(self.request.user)
			if form.is_valid() and form2.is_valid():
				# Billing Address
				street_address = form.cleaned_data.get('street_address')
				print('Billing Street Address',street_address)
				second_address = form.cleaned_data.get('second_address')
				print('Billing Street Address',second_address)
				country = form.cleaned_data.get('country')
				zip_code = form.cleaned_data.get('zip_code')
				same_billing_address = form.cleaned_data.get('same_billing_address')
				save_info = form.cleaned_data.get('save_info')
				# payment_option = form.cleaned_data.get('payment_option')
				billing_address = Address(
					user = self.request.user,
					street_address = street_address,
					second_address = second_address,
					country = country,
					zip_code = zip_code,
					address_type = 'B',
				)
				billing_address.save()
				# Shipping Address
				street_address2 = form2.cleaned_data.get('street_address')
				print('Shipping Address',street_address2)
				second_address2 = form2.cleaned_data.get('second_address')
				print('Billing Street Address',second_address2)
				country2 = form2.cleaned_data.get('country')
				zip_code2 = form2.cleaned_data.get('zip_code')				
				save_info2 = form2.cleaned_data.get('save_info')
				payment_option = form2.cleaned_data.get('payment_option')
				print('Payment Option',payment_option)
				shipping_address = Address(
					user = self.request.user,
					street_address = street_address2,
					second_address = second_address2,
					country = country2,
					zip_code = zip_code2,					
					address_type = 'S',
				)
				shipping_address.save()
				# Save Addresses in the order
				order.billing_address = billing_address
				order.shipping_address = shipping_address
				order.save()

				if payment_option == 'S':
					return redirect("app:payment",payment_option = 'stripe')
				return redirect("app:checkout")

			messages.warning(self.request,'Failed to checkout')
			return redirect("app:checkout")


		except ObjectDoesNotExist:
			messages.error(self.request,"You do not have an active order")
			return redirect("app:order-summary") 

class PaymentView(View):

	def get(self,*args,**kwargs):
		order = Order.objects.get(user = self.request.user,ordered = False)
		context = {
			'order' : order,
			
		}
	
		return render(self.request, "payment.html",context)

	def post(self,*args,**kwargs):
		
		order = Order.objects.get(user=self.request.user,ordered=False)
		token = self.request.POST.get("stripeToken")
		# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
		amount = int(order.total() * 100)
		try:
		  # Use Stripe's library to make requests...
			charge = stripe.Charge.create(
			  amount=amount,
			  currency="usd",
			  source=token	
			)	
			order.ordered = True
			# create payment 
			payment = Payment()
			payment.stripe_id = charge['id']
			payment.user = self.request.user
			payment.amount = order.total()
			payment.save()

			order_item = order.items.all()
			order_item.update(ordered=True)
			for item in order_item:
				item.save()
			order.payment = payment
			order.ref_code = reference_code()
			order.save()	

			return redirect("/")
		except stripe.error.CardError as e:
		  # Since it's a decline, stripe.error.CardError will be caught
		  body = e.json_body
		  err = body.get('error',{})
		  messages.error(self.request,f"{err.get('message')}")
		  # print('Status is: %s' % e.http_status)
		  # print('Type is: %s' % e.error.type)
		  # print('Code is: %s' % e.error.code)
		  # # param is '' in this case
		  # print('Param is: %s' % e.error.param)
		  # print('Message is: %s' % e.error.message)
		except stripe.error.RateLimitError as e:
		  # Too many requests made to the API too quickly
		  messages.error(self.request, "Rate Limit Error")
		  return redirect("/")

		except stripe.error.InvalidRequestError as e:
		  # Invalid parameters were supplied to Stripe's API
		  messages.error(self.request,"Invalid Requset Error")
		  return redirect("/")

		except stripe.error.AuthenticationError as e:
		  # Authentication with Stripe's API failed
		  # (maybe you changed API keys recently)
		  messages.error(self.request,"Authentication Error")
		  return redirect("/")

		except stripe.error.APIConnectionError as e:
		  # Network communication with Stripe failed
		  messages.error(self.request,"API connection Error")
		  return redirect("/")

		except stripe.error.StripeError as e:
		  # Display a very generic error to the user, and maybe send
		  # yourself an email
		  messages.error(self.request,"Stripe Error")
		  return redirect("/")

		except Exception as e:
		  # Something else happened, completely unrelated to Stripe
		  messages.error(self.request,"Exception")
		  return redirect("/")

def get_coupon(request,code):
	try:
		coupon = Coupon(code = code)

		return coupon

	except ObjectDoesNotExist:
		messages.info(request,"This coupon does not exist")
		return redirect("app:checkout")

def add_coupon(request):
	if request.method == "POST":
		form = CouponForm(request.POST or None)
		if form.is_valid():
						
			try:
				code = form.cleaned_data.get('code')	
				amount = form.cleaned_data.get('amount')			
				order = Order.objects.get(user=request.user,ordered=False)
				coupon = Coupon(code = code)				
				coupon.save()
				order.coupon = coupon
				# get_coupon(request,code)				
				order.save()
				messages.info(request,"successfully added")
				return redirect("app:checkout")

			except ObjectDoesNotExist:
				messages.info(request,"You dont have an active order")
				return redirect("app:checkout")

class RequestRefundView(View):

	def get(self,*args,**kwargs):
		form = RequestRefundForm()
		context = {
			'form' : form
		}
		return render(self.request,"request_form.html",context)

	def post(self,*args,**kwargs):
		form = RequestRefundForm(self.request.POST)
		
		if form.is_valid():			
			ref_code = form.cleaned_data.get('ref_code')
			message = form.cleaned_data.get('message')
			email = form.cleaned_data.get('email')

			try:
				order = Order.objects.get(ref_code = ref_code)
				print('Order',order)
				order.refund_requested = True
				order.save()

				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()

				messages.info(self.request,"You request has been sent successfully")
				return redirect("app:request-refund")

			except ObjectDoesNotExist:
				messages.info(self.request,"This order does not exist")
				return redirect("app:request-refund")