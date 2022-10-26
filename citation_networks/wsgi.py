"""
WSGI config for citation_networks project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
sys.path.append("/home/wabarr/django/citation_networks/")
sys.path.append("/home/wabarr/django/citation_networks/citation_networks/")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citation_networks.settings')

application = get_wsgi_application()
