from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
PROMO_CODE_LIST = settings.PROMO_CODE_LIST

def get_promo_code(user_promo):

    valid = False
    for code in PROMO_CODE_LIST:
        if code == user_promo:
            valid = True
    
    return valid

def get_category(Category, id, slug):

	try:
		category = Category.objects.filter(slug = slug)
		 
		if not category[0].is_leaf_node():
			 
			category = category.get_descendants(include_self=False)
			category = [i for i in category]
			return category
		else:		 
			return category[0]
	except ObjectDoesNotExist:
		return None

def is_ordered(ordered_date, status_changed):

    ordered = []
    if status_changed:
        return True

    else:
        timediff = timezone.now() - ordered_date
    
        if timediff.total_seconds() > 18000:
            return True
        else:
            return False

def filter_by_search(items,query):		
	return items.search(query)

def get_attributes(items,request):
   
    colors = []
    sizes = []
    gas_types = []
    conditions = []
    production_year_from = request.GET.get('year-from')
    production_year_to = request.GET.get('year-to')
    price_from = request.GET.get('price-from')
    price_to = request.GET.get('price-to')

    for item in items:
        
        if request.GET.get('color-{}'.format(item.color)) is not None and request.GET.get('color-{}'.format(item.color)) not in colors:
            colors.append(request.GET.get('color-{}'.format(item.color)))

        if request.GET.get('size-{}'.format(item.size)) is not None and request.GET.get('size-{}'.format(item.size)) not in sizes:
            sizes.append(request.GET.get('size-{}'.format(item.size)))

        if request.GET.get('gas_type-{}'.format(item.gas_type)) is not None and request.GET.get('gas_type-{}'.format(item.gas_type)) not in gas_types:
            gas_types.append(request.GET.get('gas_type-{}'.format(item.gas_type)))

        if request.GET.get('condition-{}'.format(item.condition)) is not None and request.GET.get('condition-{}'.format(item.condition)) not in conditions:
            conditions.append(request.GET.get('condition-{}'.format(item.condition)))
        
    return colors, price_from, price_to, sizes, production_year_from, production_year_to, gas_types, conditions
	
	 
def initialize_default_attribute_values(items, request):
    
    form_data = get_attributes(items,request)
   
    default_values_of_attributes = get_default_values_of_attributes(items) 
    
    for index, values in enumerate(form_data):
        if values:
            default_values_of_attributes[index] = values             
   
    return default_values_of_attributes

def get_default_values_of_attributes(items):
    
    try:
    
        year_from = items.order_by('-production_year').reverse()[0].production_year
        year_to = items.order_by('-production_year')[0].production_year
        gas_types = [gas for gas in items.values_list('gas_type',flat=True).distinct()]
        conditions = [condition for condition in items.values_list('condition',flat=True).distinct()]    
        colors = [color for color in items.values_list('color',flat=True).distinct()]    
        sizes = [size for size in items.values_list('size', flat=True).distinct()]        
        price_from = items.order_by('-price').reverse()[0].price
        price_to = items.order_by('-price')[0].price

    except IndexError:
        year_from = []
        year_to = []
        gas_types = []
        conditions = []
        colors = []
        price_from = []
        price_to = []
        sizes = []    
     
    return [colors, price_from, price_to, sizes, year_from, year_to, gas_types, conditions] 
    
def filter_by_items(items, request):
    default_values_attributes = initialize_default_attribute_values(items, request)
    
    try:
        items = items.filter(price__range = (default_values_attributes[1],default_values_attributes[2]))
       
        if items[0].category.get_root().title == "Transport" and items[0].category.title != "Car parts":
            
            return items.filter(color__in = [color for color in default_values_attributes[0]], 
                                gas_type__in = [gas_type for gas_type in default_values_attributes[6]],
                                condition__in = [condition for condition in default_values_attributes[7]],
                                production_year__range = (default_values_attributes[4], default_values_attributes[5]),
                            )

        elif items[0].category.get_root().title == 'Apparel':
            
            return items.filter(color__in = [color for color in default_values_attributes[0]], 
                                size__in = [size for size in default_values_attributes[3]]
                            )
    except IndexError:
        
        return items
    except TypeError:
      
        return items
    