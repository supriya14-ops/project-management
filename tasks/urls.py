from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('create/<int:project_id>/', views.create_task, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_task, name='edit'),
    path('<int:pk>/update-status/', views.update_task_status, name='update_status'),
]
