"""
URL configuration for Viviz Bulk Sender project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API authentication
    path('api/auth/', include('apps.authentication.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # App APIs
    path('api/', include('apps.tenants.urls')),
    path('api/', include('apps.contacts.urls')),
    path('api/', include('apps.campaigns.urls')),
    path('api/', include('apps.messages.urls')),
    path('api/', include('apps.chats.urls')),
    path('api/', include('apps.analytics.urls')),
    path('api/', include('apps.subscriptions.urls')),
    path('api/', include('apps.green_api.urls')),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
