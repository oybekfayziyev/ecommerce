from django.shortcuts import render
from .models import Item,Order,OrderItem
from django.views.generic import ListView,DetailView,View
from django.shortcuts import get_object_or_404,redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from app.forms import CheckoutForm
# Create your views here.

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
			message.error(self.request,"You do not have an active order")
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
		forms = {
			'form' : form
		}
		return render(self.request,"checkout-page.html",forms)

	def post(self,*args,**kwargs):
		form = CheckoutForm(self.request.POST or None)
		if form.is_valid():
			print(form.cleaned_data)
			return redirect(self.request,"app:checkout")

		return redirect(self.request,"app:checkout")