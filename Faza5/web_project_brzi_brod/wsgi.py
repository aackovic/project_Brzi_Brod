# Andrej Ačković 0263/2021

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_project_brzi_brod.settings")

application = get_wsgi_application()
