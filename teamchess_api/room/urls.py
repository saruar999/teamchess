from django.urls import path
from . import views

urlpatterns = [
    path('room/', views.ListCreateRoomView.as_view()),
    path('room/<uuid:pk>/', views.RetrieveRoomView.as_view()),
    path('room/<uuid:pk>/join/', views.JoinRoomView.as_view()),
    path('player/<int:pk>/kick/', views.KickPlayerView.as_view())
]
