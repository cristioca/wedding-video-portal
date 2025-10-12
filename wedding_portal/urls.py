"""
URL configuration for wedding_portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from projects import views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching endpoint
]

# Add language-prefixed URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', include('projects.urls')),
    prefix_default_language=True,  # Add /en/ prefix for English (explicit language URLs)
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
