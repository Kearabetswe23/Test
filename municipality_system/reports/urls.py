from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.report_list, name='report_list'),
    path('new/', views.report_create, name='report_create'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('inbox/', views.messages_inbox, name='messages_inbox'),
]
