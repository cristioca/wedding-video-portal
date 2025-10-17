from django.urls import path
from . import views

urlpatterns = [
    # Specific paths must come before generic slug pattern
    path('create/', views.create_project, name='create_project'),
    path('archived/', views.archived_projects, name='archived_projects'),
    path('backup/', views.backup_database, name='backup_management'),
    path('backup/download/<str:filename>/', views.download_backup, name='download_backup'),
    path('backup/delete/<str:filename>/', views.delete_backup, name='delete_backup'),
    path('file/<int:file_id>/download/', views.download_file, name='download_file'),
    path('modification/<int:mod_id>/approve/', views.approve_modification, name='approve_modification'),
    
    # Slug-based action paths (must come before the generic slug detail view)
    path('<str:slug>/notify/', views.notify_client, name='notify_client'),
    path('<str:slug>/clear-notification/', views.clear_notification, name='clear_notification'),
    path('<str:slug>/send-credentials/', views.send_credentials, name='send_credentials'),
    path('<str:slug>/change-client-data/', views.change_client_data, name='change_client_data'),
    path('<str:slug>/update-field/', views.update_project_field, name='update_project_field'),
    path('<str:slug>/batch-update/', views.batch_update_project, name='batch_update_project'),
    path('<str:slug>/update-field-order/', views.update_field_order, name='update_field_order'),
    path('<str:slug>/field-history/<str:field_name>/', views.get_field_history, name='get_field_history'),
    path('<str:slug>/dismiss-guidance/', views.dismiss_guidance, name='dismiss_guidance'),
    path('archive/<str:slug>/', views.archive_project, name='archive_project'),
    path('delete/<str:slug>/', views.delete_project, name='delete_project'),
    
    # Generic slug detail view (MUST be last)
    path('<str:slug>/', views.project_detail, name='project_detail'),
]
