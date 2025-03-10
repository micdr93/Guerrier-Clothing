from django.conf import settings
from django.views.static import serve

def serve_media_in_production(request, path, document_root=None):
    """Custom view to serve media files in production"""
    return serve(request, path, document_root=settings.MEDIA_ROOT)