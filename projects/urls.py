from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('create/', views.create_project, name='create_project'),
    path('archive/<int:pk>/', views.archive_project, name='archive_project'),
    path('delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('archived/', views.archived_projects, name='archived_projects'),
    path('file/<int:file_id>/download/', views.download_file, name='download_file'),
    path('<int:pk>/notify/', views.notify_client, name='notify_client'),
    path('<int:pk>/clear-notification/', views.clear_notification, name='clear_notification'),
    path('<int:pk>/send-credentials/', views.send_credentials, name='send_credentials'),
    path('<int:pk>/change-client-data/', views.change_client_data, name='change_client_data'),
    path('<int:pk>/update-field/', views.update_project_field, name='update_project_field'),
    path('<int:pk>/update-field-order/', views.update_field_order, name='update_field_order'),
    path('modification/<int:mod_id>/approve/', views.approve_modification, name='approve_modification'),
]
