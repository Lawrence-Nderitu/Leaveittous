from django.urls import path
from . import views

app_name = 'landing_page'
urlpatterns = [
    path('', views.landing_page_view, name='landing_page'),

    # Old generic paths (commented out for now, can be removed later)
    # path('register/', views.register_view, name='register'),
    # path('login/', views.login_view, name='login'),

    # New Role-Specific Registration Paths
    path('register/student/', views.student_register_view, name='student_register'),
    path('register/writer/', views.writer_register_view, name='writer_register'),
    # path('register/admin/', views.admin_register_view, name='admin_register'), # Optional for admin

    # New Role-Specific Login Paths
    path('login/student/', views.student_login_view, name='student_login'),
    path('login/writer/', views.writer_login_view, name='writer_login'),
    # path('login/admin/', views.admin_login_view, name='admin_login'), # Optional for admin

    path('logout/', views.logout_view, name='logout'),
]
