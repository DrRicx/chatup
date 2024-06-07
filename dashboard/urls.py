from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='login'),
    path('logount/', views.admin_logout, name='logout'),
    path('admin/', views.admin_index_view, name='admin_index'),
]
