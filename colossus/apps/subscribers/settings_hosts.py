from django.conf import settings 

ALLOWED_HOSTS = getattr(settings, 'ALLOWED_HOSTS', [])