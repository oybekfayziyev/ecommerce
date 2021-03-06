from django import template
from app.models import Order
from django.shortcuts import reverse

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
	
	return value1 - value2

@register.filter
def get_slug(item):
	print('slug',item.slug)
	slug = item.slug
	return reverse("app:product", kwargs={"slug": slug})

@register.filter
def add_to_card_url_tags(item):
	slug = item.slug
	return reverse("app:add-to-card",kwargs = {
			'slug' : slug
			})
	 
@register.filter
def get_first_element(item):
	return item[0]

@register.filter
def get_root(category):
	return category.get_root()

@register.filter
def get_children(category):
	return category.get_children()

