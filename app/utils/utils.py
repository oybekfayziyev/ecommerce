from django.utils.text import slugify
import string
import random, os

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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_file_ext(filepath):
    base_name = os.path.basename(filepath)
    print('base',base_name)
    name, ext = os.path.splitext(base_name)

    return name, ext

def upload_image_path(instance, filename):
    print('filename',filename)
    new_filename = random.randint(1,3910209312)
    name, ext = get_file_ext(filename)
    print(name)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{new_filename}/{final_filename}".format(
            new_filename=new_filename, 
            final_filename=final_filename
            )

    