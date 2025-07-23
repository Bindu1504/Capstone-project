from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/book/', views.book_event, name='book_event'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('review/<int:booking_id>/', views.add_review, name='add_review'),
    path('api/ticket-info/', views.get_ticket_info, name='get_ticket_info'),
path('ajax/filter/', views.ajax_event_filter, name='event_filter'),
path('login/', auth_views.LoginView.as_view(), name='login'),
path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
path('booking/<int:booking_id>/pay/', views.payment_page, name='payment_page'),
path('booking/<int:booking_id>/download/', views.download_ticket, name='download_ticket'),
path('subscribe/', views.subscribe, name='subscribe'),
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]