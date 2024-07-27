from django.urls import path
from . import views


urlpatterns = [
    path('<int:pk>/kick/', views.KickPlayerView.as_view()),
    path('<int:pk>/change_team/', views.ChangePlayerTeamView.as_view()),
    path('<int:pk>/swap_player/', views.SwapPlayerView.as_view())
]
