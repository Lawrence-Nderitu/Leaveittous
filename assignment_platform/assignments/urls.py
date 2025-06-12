from django.urls import path
from . import views

app_name = 'assignments'
urlpatterns = [
    path('new/', views.create_assignment_view, name='create_assignment'),
    path('<int:assignment_id>/student_detail/', views.assignment_detail_student_view, name='assignment_detail_student'),
    path('browse/', views.browse_open_assignments_view, name='browse_open_assignments'),
    path('<int:assignment_id>/writer_detail/', views.assignment_detail_writer_view, name='assignment_detail_writer'),
    path('bid/<int:bid_id>/award/', views.award_assignment_view, name='award_assignment'),
    path('<int:assignment_id>/submit/', views.submit_assignment_view, name='submit_assignment'),
    path('<int:assignment_id>/complete/', views.mark_assignment_complete_view, name='mark_assignment_complete'),
]
