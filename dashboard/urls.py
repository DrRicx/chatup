from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_login, name='login'),
    path('logount/', views.admin_logout, name='logout'),
    path('admin/', views.admin_index_view, name='admin_index'),
    path('admin/users/', views.user_list_view, name='user_list'),
    path('admin/users/add/', views.user_add_view, name='user_add'),
    path('admin/users/edit/<int:pk>/', views.user_change_view, name='user_edit'),
    path('admin/<str:app_label>/<str:model_name>/', views.model_list_view, name='model_list'),
    path('admin/<str:app_label>/<str:model_name>/add/', views.model_form, name='model_add'),
    path('admin/<str:app_label>/<str:model_name>/<int:object_id>/', views.model_form, name='model_edit'),
]
