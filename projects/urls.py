from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('create/', views.create_project, name='create_project'),
    path('<int:pk>/archive/', views.archive_project, name='archive_project'),
    path('file/<int:file_id>/download/', views.download_file, name='download_file'),
    path('<int:pk>/notify/', views.notify_client, name='notify_client'),
    path('<int:pk>/update-field/', views.update_project_field, name='update_project_field'),
    path('modification/<int:mod_id>/approve/', views.approve_modification, name='approve_modification'),
]
