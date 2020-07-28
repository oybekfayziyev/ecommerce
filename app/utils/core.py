from django.conf import settings

PROMO_CODE_LIST = settings.PROMO_CODE_LIST

def get_promo_code(user_promo):

    valid = False
    for code in PROMO_CODE_LIST:
        if code == user_promo:
            valid = True
    
    return valid

