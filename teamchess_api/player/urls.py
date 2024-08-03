from django.urls import path
from . import views


urlpatterns = [
    path('', views.PlayerInfoView.as_view()),
    path('<int:pk>/kick/', views.KickPlayerView.as_view()),
    path('<int:pk>/change_symbol/', views.ChangePlayerSymbolView.as_view()),
]
