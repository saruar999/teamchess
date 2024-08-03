from django.urls import path
from . import views


urlpatterns = [
    path('', views.StartGameView.as_view())
]