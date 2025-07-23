from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.project_list, name='list'),
    path('create/', views.create_project, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/invite/', views.invite_member, name='invite_member'),
    path('invitation/<int:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
]
