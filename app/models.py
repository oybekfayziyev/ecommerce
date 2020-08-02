from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.db.models.signals import pre_save
from django.db.models import Q
from .utils.utils import generate_unique_slug

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session

from .utils.utils import get_client_ip, upload_image_path
from .utils.signals import object_viewed_signal,user_logged_in

from mptt.models import MPTTModel, TreeForeignKey

FORCE_SESSION_TO_ONE = getattr(settings, 'FORCE_SESSION_TO_ONE', False)
FORCE_INACTIVE_USER_ENDSESSION= getattr(settings, 'FORCE_INACTIVE_USER_ENDSESSION', False)


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

ADDRESS_CHOICES = (
	('S', 'Shipping'),
	('B', 'Billing')
)

class ItemQuerySet(models.QuerySet):

	def search(self, query):
		
		lookups = (Q(title__icontains=query) | 
					Q(price__icontains=query) |
					Q(category__title__icontains=query) |
					Q(description__icontains=query))
	
		return self.filter(lookups).distinct()
		# return super().filter(title__icontains=query)

class ItemExtraImage(models.Model):
	title = models.CharField(max_length = 64, null=True,blank=True)
	image = models.ImageField(upload_to = upload_image_path)
	item = models.ForeignKey('Item', null=True,blank=True, on_delete=models.CASCADE, related_name='images')

	class Meta:
		verbose_name_plural = 'Images'

class ItemManager(models.Manager):

	def get_queryset(self):
		return ItemQuerySet(self.model, using=self._db)
	
	def search(self,query):
		return self.get_queryset().search(query)

class Item(models.Model):
	title = models.CharField(max_length=100)
	price = models.FloatField()
	discount_price = models.FloatField(blank=True,null=True)
	category = models.ForeignKey('Category', on_delete=models.CASCADE)
	label = models.CharField(choices=LABEL_CHOICES,max_length=1)
	description = models.TextField()
	slug = models.SlugField(blank=True, null=True)
	image = models.ImageField(upload_to = upload_image_path, blank=True,null=True)
	
	objects = ItemManager()

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
	
class Category(MPTTModel):
	title = models.CharField(max_length=30)
	keywords = models.CharField(max_length = 255, blank=True, null=True)
	description =models.CharField(max_length = 255, blank=True, null=True)
	image = models.ImageField(upload_to = 'product/categories', blank=True,null=True)
	parent = TreeForeignKey('self',on_delete = models.CASCADE, blank=True,null=True, related_name = 'children')
	status = models.BooleanField(default = True)
	slug = models.SlugField(blank = True, null = True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

	# def get_children_tree(self):
	# 	return self.get_children()
	class MPTTMeta:
		order_insertion_by = 'title'
	
	class Meta:
		verbose_name_plural = 'Categories'

def generate_slug(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = generate_unique_slug(instance)

pre_save.connect(generate_slug, sender = Item)
pre_save.connect(generate_slug, sender = Category)


class OrderItem(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
	ordered = models.BooleanField(default=False)
	item = models.ManyToManyField(Item)
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


class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE)
	street_address = models.CharField(max_length = 30)
	second_address = models.CharField(max_length = 30)
	country = CountryField(multiple=False)
	zip_code = models.CharField(max_length = 30)
	address_type = models.CharField(max_length=1,choices = ADDRESS_CHOICES)
	default = models.BooleanField(default=False)


	def __str__(self):
		return self.user.username

	class Meta:
		verbose_name_plural = 'Addresses'


class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default = False)
	billing_address = models.ForeignKey('Address', related_name = 'billing_address', on_delete = models.SET_NULL, blank=True, null=True)
	shipping_address = models.ForeignKey('Address', related_name = 'shipping_address', on_delete = models.SET_NULL, blank=True, null=True)
	payment = models.ForeignKey('Payment', on_delete = models.SET_NULL, blank=True, null = True)
	coupon = models.ForeignKey('Coupon',on_delete = models.SET_NULL,blank = True,null=True)
	being_delivered = models.BooleanField(default = False)
	received = models.BooleanField(default = False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default = False)
 
	def __str__(self):
		return f"{self.user}"

	def total(self):
		total = 0
		for order_item in self.items.all():			 
			total += order_item.get_final_price()
		if self.coupon:
			total -= self.coupon.amount 
		if total < 0:
			total = 0
		return total

class Payment(models.Model):
	stripe_id = models.CharField(max_length = 30)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE)
	amount = models.FloatField()
	timestamp = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.user.username;

class Coupon(models.Model):	
	code = models.CharField(max_length=30)
	amount = models.FloatField(default=0)

	def __str__(self):
		return self.code

class Refund(models.Model):

	order = models.ForeignKey(Order,on_delete=models.CASCADE)
	reason = models.TextField()
	accepted = models.BooleanField(default=False)
	email = models.EmailField()

	def __str__(self):
		return f"{self.pk}"

class ObjectViewed(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ip_address = models.CharField(max_length = 50)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "%s viewed on %s"%(self.content_type, self.timestamp)
	
	class Meta:
		ordering = ['-timestamp']
		verbose_name = 'Object Viewed'
		verbose_name_plural = 'Objects Viewed'

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
	content_type = ContentType.objects.get_for_model(sender)
	new_view_obj = ObjectViewed.objects.create(
		user = request.user,
		content_type = content_type,
		object_id = instance.id,
		ip_address = get_client_ip(request)
	)
object_viewed_signal.connect(object_viewed_receiver)

class UserSession(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
	ip_address = models.CharField(max_length = 64, blank=True, null = True)
	session = models.CharField(max_length = 128, blank = True, null = True)
	active = models.BooleanField(default=True)
	ended = models.BooleanField(default = False)
	timestamp = models.DateTimeField(auto_now_add=True)

	def endsession(self):
		try:
			session = Session.objects.get(pk = self.session).delete()
			self.active = False
			self.ended = True
			self.save()
		except:
			pass
		return self.ended

def post_save_session_receiver(sender, instance, created, *args, **kwargs):

	if created:
		session = Session.object.filter(user = instance.user, active = False, ended = False).exclude(id=instance.id)

		for i in session:
			i.endsession()
	
	if not instance.active and instance.ended:
		instance.endsession()

if FORCE_SESSION_TO_ONE:
    post_save.connect(post_save_session_receiver, sender=UserSession)

def post_save_user_changed_receiver(sender, instance, created, *args, **kwargs):
    if not created:
        if instance.is_active == False:
            qs = UserSession.objects.filter(user=instance.user, ended=False, active=False)
            for i in qs:
                i.endsession()


if FORCE_INACTIVE_USER_ENDSESSION:
    post_save.connect(post_save_user_changed_receiver, sender=User)

def user_logged_in_receiver(sender, instance, request, *args, **kwargs):
    user = instance
    ip_address = get_client_ip(request)
    session_key = request.session.session_key # Django 1.11
    UserSession.objects.create(
            user=user,
            ip_address=ip_address,
            session=session_key
        )


# user_logged_in.connect(user_logged_in_receiver)