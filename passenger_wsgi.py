# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u1919191/data/www/ihubzone.ru/mir4')
sys.path.insert(1, '/var/www/u1919191/data/djangoenv/lib/python3.10/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mir4.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()