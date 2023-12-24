# agrochat/asgi.py

# agrochat/asgi.py

import os
from django.core.asgi import get_asgi_application
from uvicorn.workers import UvicornWorker  # Importe a classe diretamente

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrochat.settings')

application = get_asgi_application()



