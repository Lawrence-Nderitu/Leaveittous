from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('dashboard/student/', views.student_dashboard_view, name='student_dashboard'),
    path('dashboard/writer/', views.writer_dashboard_view, name='writer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/manage/users/', views.admin_list_users_view, name='admin_list_users'),
    path('admin/users/<int:user_id>/toggle-activation/', views.toggle_user_activation_view, name='toggle_user_activation'),
]
