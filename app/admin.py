from django.contrib import admin
from .models import (Order, OrderItem, 
					Item,Address,Payment,
					Coupon,Refund, ObjectViewed, 
					Category, ItemExtraImage)
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html
# Register your models here.

def make_refund_accepted(modeladmin,request,queryset):
	queryset.update(refund_requested=False,refund_granted=True)

make_refund_accepted.short_description = 'Update orders to refund granted'

class OrderAdmin(admin.ModelAdmin):
	list_display = ['user',
					'ordered',
					'being_delivered',
					'received',
					'refund_requested',
					'refund_granted',
					'billing_address',
					'payment',
					'coupon'
		]
	list_display_links = [
		'user',
		'billing_address',
		'payment',
		'coupon'
	]
	list_filter = [
		'ordered',
		'being_delivered',
		'received',
		'refund_requested',
		'refund_granted'
	]
	search_fields = [
		'user__username',
		'ref_code'
	]

	actions = [make_refund_accepted]

class OrderItemAdmin(admin.ModelAdmin):
	list_display = [
		'item','user','quantity','ordered'
	]

class AddressAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'street_address',
		'second_address',
		'country',
		'zip_code',
		'address_type',
		'default'
	]
	list_filter = ['default','address_type','country']
	search_fields = ['user','street_address','second_address','zip_code']

class ItemImageInline(admin.TabularInline):
	model = ItemExtraImage
	extra = 5

class ItemAdmin(admin.ModelAdmin):

	def image_tag(self, obj):
		return format_html('<img src="{}" height="50px" width="50px"/>'.format(obj.image.url))
    
	image_tag.short_description = 'Image'
 
	list_display = [
		'title',
		'category',	
		'price',
		'image_tag'
	]
	inlines = [ItemImageInline]

class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_item_count', 'related_item_cumulative_count')
    list_display_links = ('indented_title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Item,
                'category',
                'item_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Item,
                 'category',
                 'item_count',
                 cumulative=False)
        return qs

    def related_item_count(self, instance):
        return instance.item_count
    related_item_count.short_description = 'Related products (for this specific category)'

    def related_item_cumulative_count(self, instance):
        return instance.item_cumulative_count
    related_item_cumulative_count.short_description = 'Related products (in tree)'

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(ObjectViewed)
admin.site.register(Category,CategoryAdmin)