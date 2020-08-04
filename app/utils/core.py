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

    

