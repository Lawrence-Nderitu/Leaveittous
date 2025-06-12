from django.urls import path
from . import views

app_name = 'landing_page'
urlpatterns = [
    path('', views.landing_page_view, name='landing_page'), # This will be landing_page:landing_page
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
