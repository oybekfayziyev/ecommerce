from django.db import models
from django.conf import settings
from django.shortcuts import reverse
# Create your models here.
CATEGORY_CHOICES = (
	('S','Shirt'),
	('SW','Sport Wear'),
	('OW','Outwear')
)
LABEL_CHOICES = (
	('P','primary'),
	('D','danger'),
	('S','secondary')
)


class Item(models.Model):
	title = models.CharField(max_length=100)
	price = models.FloatField()
	discount_price = models.FloatField(blank=True,null=True)
	category = models.CharField(choices = CATEGORY_CHOICES,max_length=2)
	label = models.CharField(choices=LABEL_CHOICES,max_length=1)
	description = models.TextField()

	slug = models.SlugField()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("app:product",kwargs = {
				'slug' : self.slug
			})

	def get_add_to_card_url(self):
		return reverse("app:add-to-card",kwargs = {
			'slug' : self.slug
			})
	def get_remove_from_card_url(self):
		return reverse("app:remove-from-card",kwargs = {
			'slug' : self.slug
			})

class OrderItem(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item,on_delete=models.CASCADE)
	quantity = models.FloatField(default=1)
	
	def __str__(self):
		return f"{self.quantity} of {self.item}"

	def get_total_item_price(self):
		return self.quantity * self.item.price 

	def get_total_discount_item_price(self):
		return self.quantity * self.item.discount_price

	def total_savings(self):
		return self.get_total_item_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_discount_item_price()
		else:
			return self.get_total_item_price();


class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default = False)

	def __str__(self):
		return f"{self.user}"

	def total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total



