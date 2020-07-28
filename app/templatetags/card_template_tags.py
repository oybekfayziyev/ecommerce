from django import template
from app.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
	
	if user.is_authenticated:
		qs = Order.objects.filter(user=user,ordered=False)		
		if qs.exists():
			return qs[0].items.count()

	return 0 

@register.filter
def multiply(value1):
	return round(value1 * 0.05)

@register.filter
def subtruct(value1, value2):
	print('value1',value1)
	print(value2)
	return value1 - value2

