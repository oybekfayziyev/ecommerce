from django.utils.text import slugify
import string

def random_str_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generate_unique_slug(instance, new_slug = None):
    if new_slug is None:
        new_slug = slugify(instance.title);
    
    Klass = instance.__class__
    qs = Klass.objects.filter(slug = new_slug).exists()

    if qs:
        new_slug = "{slug}-{random_str}".format(new_slug, random_str_generator(size=4))

        return generate_unique_slug(instance,new_slug=new_slug)
    
    return new_slug


    