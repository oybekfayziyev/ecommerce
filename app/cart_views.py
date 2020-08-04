from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect
from .models import Order, OrderItem, Item
from django.contrib import messages
from django.utils import timezone

@login_required
def add_to_card_summary(request, slug):
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
			order_item.delete()
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
def remove_single_item_from_card(request, slug):
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
				order_item.delete()
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
def remove_all_item_from_card(request, slug):
	item = get_object_or_404(Item,slug=slug)
	order_qs = Order.objects.filter(user=request.user,ordered=False)

	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug = item.slug).exists():
			messages.info(request,"Order removed successfully")
			order_item = OrderItem.objects.filter(user=request.user,item=item,ordered=False)[0]	
			
			order.items.remove(order_item)
			order_item.delete()
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

