from django.urls import path
from . import views

urlpatterns = [
    path('/', views.ListCreateRoomView.as_view()),
    path('/<uuid:pk>/', views.RetrieveRoomView.as_view()),
]
