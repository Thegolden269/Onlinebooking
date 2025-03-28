from django.urls import path
from . import views

urlpatterns = [
    path('reservations/create', views.create_reservation_view, name='create_reservation'),
    path('creneaux/', views.available_creneaux_view, name='list-reservations'),
    path('reservations/<str:numero_reservation>/update/', views.update_reservation_view, name='update-reservation'),
    path('reservations/<str:numero_reservation>/cancel/', views.cancel_reservation_view, name='cancel-reservation'),
    path('reservations/<str:numero_reservation>/', views.retrieve_reservation_view, name='retrieve-reservation'),
]
