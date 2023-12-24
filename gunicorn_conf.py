# gunicorn_conf.py




def on_starting(server):
    server.log.info("Loading Django settings")
    import os
    from django.core.wsgi import get_wsgi_application


    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrochat.settings")
    get_wsgi_application()

import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "127.0.0.1:8000"
chdir = "."
module = "agrochat.asgi"
