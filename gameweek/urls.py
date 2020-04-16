from django.urls import path

from . import views

app_name = 'games'
urlpatterns = [
    # ex: /games/
    path('', views.index, name='index'),
    # ex: /games/5/
    path('<int:game_id>/', views.detail, name='detail'),
    # ex: /games/results/5/
    path('results/<int:game_id>/', views.results, name='results'),
    # ex: /games/predict/5
    path('predict/<int:game_id>/', views.predict, name='predict'),
]