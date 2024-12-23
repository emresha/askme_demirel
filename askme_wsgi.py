import os


def askme(environ, start_response):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "askme_demirel.settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    return application(environ, start_response)

application = askme