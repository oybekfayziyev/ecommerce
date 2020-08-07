from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .models import Item,Order,OrderItem
from django.views.generic import ListView,DetailView,View, TemplateView
from django.shortcuts import get_object_or_404,redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.mixins import LoginRequiredMixin
from app.forms import CheckoutForm, CouponForm, RequestRefundForm, RequestRefundedForm
from .models import Address,Payment,Coupon,Refund, Category
from .mixins import ObjectViewedMixin
from .exceptions import ImmediateHttpResponse
from allauth.account.views import LoginView

from .utils.utils import reference_code, is_valid_form
from .utils.core import (get_promo_code, is_ordered,						
						get_category)
# Create your views here.

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY




class HomeView(ListView):
	 
	paginate_by = 9
	template_name = 'home.html'

	def get_context_data(self, *args, **kwargs):
		context = super(HomeView,self).get_context_data(*args, **kwargs)
		query = self.request.GET.get('search')		
		category = Category.objects.all()
		context["query"] = query
		context['category'] = category
		return context
	
	def get_queryset(self, *args, **kwargs):

		query = self.request.GET.get('search', None)	 
		if query is not None:
						 
			return Item.objects.search(query)
	 
		return Item.objects.all()
	
	

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
	 
	template_name = 'product-page.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)			 
		root_nodes = Category.objects.root_nodes()
	 
		node = Category.objects.get(title = self.get_object().category)
		root = node.get_root()
		siblings = node.get_siblings(include_self=True)	
		related_items = Item.objects.filter(category__in = [i for i in siblings]) 	
		context['category'] = related_items		 
		return context
	

	def get_object(self, *args, **kwargs):
		try:
			item = Item.objects.get(slug = self.kwargs.get('slug'))	
				
		except ObjectDoesNotExist:
			messages.info(self.request, "Product slug is not found")
			return redirect('/')
		

		return item

	def get_queryset(self):

		return super().get_queryset()
	

class CategoryDetailView(DetailView):

	template_name = 'category_product.html'
	paginated_by = 9

	def get_object(self, *args, **kwargs):

		try:
			elements = get_category(Category, self.kwargs.get('id'), self.kwargs.get('slug'))			 
			category = Category.objects.filter(title__in = elements)			
			items = Item.objects.filter(category__in = category)
					 
		except TypeError:			 
			category = Category.objects.filter(title = elements)			 
			items = Item.objects.filter(category = category[0])
			 	
		return items

	def get_context_data(self, *args, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
		category = get_category(Category, self.kwargs.get('id'), self.kwargs.get('slug'))	
		category_ = Category.objects.get(slug= self.kwargs.get('slug'))		 
		query = self.request.GET.get('search')	
		print('query',query)	 
		context["query"] = query
		context['category'] = category
		context['category_'] = category_	
			 
		return context
	
	def get_queryset(self, *args, **kwargs):

		query = self.request.GET.get('search', None)	 
		if query is not None:
						 
			return Item.objects.search(query)
	 
		return Item.objects.all()

class OrderedItems(ListView):
	 
	template_name = 'ordered.html'
	
	def get_queryset(self):
		is_product_ordered = []
		orders = Order.objects.filter(user = self.request.user, ordered = True).order_by('-ordered_date')
		
		for order in orders:
			is_product_ordered.append(is_ordered(order.ordered_date, order.status_changed))
		# is_product_ordered = is_ordered([date.ordered_date for date in orders])
		print(is_product_ordered)
		for index, i in enumerate(is_product_ordered):
			
			if i:			 			
				orders[index].being_delivered = False
				orders[index].received = True
			else:			 
				orders[index].being_delivered = True
				orders[index].received = False
			
			orders[index].save()
		return orders
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		context["orders"] = self.get_queryset()	
		
		return context	

class OrderStatus(View):

	def get(self, *args, **kwargs):

		return render(self.request, 'order_status.html' )
	 
	def post(self, *args, **kwargs):
		order_id = self.kwargs.get('id')
		try:
			order = Order.objects.get(id = order_id)
			 
			order.being_delivered = False
			order.received = True
			order.status_changed = True
			order.save()
			 
			messages.info(self.request, "{} order status has been changed to Received".format(order))
			return redirect('app:ordered-items')
		except ObjectDoesNotExist:
			messages.info(self.request, "Order id is not valid")
			return redirect("app:ordered-items")
class Checkout(View):
	
	def get(self,*args,**kwargs):
		billing_form = CheckoutForm()	
		try:
			if not self.request.user.is_authenticated:
				return redirect("account_login")
			order = Order.objects.get(user = self.request.user,ordered=False)
						
			context = {
				'form' : billing_form,					 
				'order' : order,
				'couponform' : CouponForm(),
			}
			shipping_address_qs = Address.objects.filter(
				user=self.request.user,
				address_type='S',
				default=True
			)


			if shipping_address_qs.exists():	
					
				context.update({'default_shipping_address': shipping_address_qs[0]})

			billing_address_qs = Address.objects.filter(
				user=self.request.user,
				address_type='B',
				default=True
			)

			if billing_address_qs.exists():
				context.update({'default_billing_address': billing_address_qs[0]})


			return render(self.request,"checkout.html",context)
		 

		except Order.DoesNotExist:
		 
			messages.info(self.request,"Order does not exist")
			return redirect("/")

		

	def post(self,*args,**kwargs):
		
		form = CheckoutForm(self.request.POST or None)
		coupon_form = CouponForm(self.request.POST or None)
		
		try:
			order = Order.objects.filter(user=self.request.user,ordered=False,items__user = self.request.user)[0]
			
			if form.is_valid():
				
				 
				use_defaul_shipping = form.cleaned_data.get('use_default_shipping')
				
				if use_defaul_shipping:
					address_qs = Address.objects.filter(
						user = self.request.user,
						address_type = 'S',
						default = True
					)

					if address_qs.exists():
						shipping_address = address_qs[0]
						order.shipping_address = shipping_address
						order.save()
					else:
						messages.info(self.request, "No default shipping address exist")
						return redirect("app:checkout")

				else:
					shipping_address1 = form.cleaned_data.get('shipping_address')
					shipping_address2 = form.cleaned_data.get('shipping_address2')
					shipping_country = form.cleaned_data.get('shipping_country')
					shipping_zip = form.cleaned_data.get('shipping_zip')
                    
					if is_valid_form([shipping_address1, shipping_address2, shipping_country, shipping_zip]):

						shipping_address = Address(
						user = self.request.user,
						street_address = shipping_address1,
						second_address = shipping_address2,
						country = shipping_country,
						zip_code = shipping_zip,
						address_type = 'S',
						)

						shipping_address.save()
						order.shipping_address = shipping_address
						order.save()

						set_default_shipping = form.cleaned_data.get('set_default_shipping')
						if set_default_shipping:
							shipping_address.default = True
							shipping_address.save()
					
					else:
						messages.info(self.request, "Please fill in the required shipping address fields ")
						return redirect('app:checkout')

				use_default_billing_address = form.cleaned_data.get('use_default_billing_address')
				same_billing_address = form.cleaned_data.get('same_billing_address')

				if same_billing_address:
					billing_address = shipping_address
					billing_address.save()
					billing_address.address_type = 'B'
					billing_address.save()
					order.billing_address = billing_address
					order.save()

				elif use_default_billing_address:
					address_qs = Address.objects.filter(
						user = request.user,
						address_type='B',
						default = True
					)

					if address_qs.exists():
						address = address_qs[0]
						order.shipping_address = address 
						order.save()
						 
					else:
						messages.info(self.request, "You don't have default billing address")
						return redirect("app:checkout")

				else:
					billing_address1 = form.cleaned_data.get('billing_address')				
					billing_address2 = form.cleaned_data.get('billing_address2')				
					billing_country = form.cleaned_data.get('billing_country')
					billing_zip = form.cleaned_data.get('billing_zip')

					if is_valid_form([billing_address1, billing_address2, billing_country, billing_zip]):
						billing_address = Address(
							user = self.request.user,
							street_address = billing_address1,
							second_address = billing_address2,
							country = billing_country,
							zip_code = billing_zip,
							address_type = 'B'
							)
						billing_address.save()

						order.billing_address = billing_address
						order.save()

						set_default_billing_address = form.cleaned_data.get('set_default_billing')
						if set_default_billing_address:
							billing_address.default = True
							billing_address.save()
					
					else:
						messages.info(self.request, "Please fill in the required billing address fields")
						return redirect('app:checkout')
				
				payment_option = form.cleaned_data.get('payment_option')
				
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
			order.ordered_date = timezone.now()
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


def add_coupon(request):
	if request.method == "POST":
		form = CouponForm(request.POST or None)
		if form.is_valid():						
			try:
				code = form.cleaned_data.get('code')
				order = Order.objects.get(user = request.user, ordered=False)		
				coupon = order.coupon	
					
				if(str(code) == str(coupon)):
					messages.info(request, "You have already used this coupon")
					return redirect('app:checkout')								
							 
				if get_promo_code(code):										
																				
					amount = round(order.total() * 0.05)
					
					coupon = Coupon(code = code, amount = amount)				
					coupon.save()
					order.coupon = coupon
					# get_coupon(request,code)				
					order.save()
					messages.info(request,"successfully added")
					return redirect("app:checkout")
				
				else:
					messages.info(request, "Coupon code is not valid")
					return redirect('app:checkout')

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
			
			message = form.cleaned_data.get('reason_for_refund')
			email = form.cleaned_data.get('email')

			try:
				order = Order.objects.get(id = self.kwargs.get('id'))
				print('Order',order)
				
				order.refund_requested = True
				order.save()

				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()

				messages.info(self.request,"You request has been sent successfully")
				return redirect("app:ordered-items")

			except ObjectDoesNotExist:
				messages.info(self.request,"This order does not exist")
				return redirect("app:ordered-items")

class RequestRefundedView(View):

	def get(self,*args,**kwargs):
		form = RequestRefundedForm()
		context = {
			'form' : form
		}
		return render(self.request,"refund_request.html",context)

	def post(self,*args,**kwargs):
		form = RequestRefundedForm(self.request.POST)
		
		if form.is_valid():			
			
			message = form.cleaned_data.get('reason_for_refund')
			email = form.cleaned_data.get('email')

			messages.info(self.request,"You refund request form has been updated")
			return redirect("app:ordered-items")

class ContactView(TemplateView):
	template_name = 'contact.html'