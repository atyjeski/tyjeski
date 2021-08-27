from django.urls import path
from . import views

app_name = 'tyjeski'
urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio-01', views.portfolio_01, name='portfolio-01'),
    path('portfolio-02', views.portfolio_02, name='portfolio-02'),
    path('portfolio-03', views.portfolio_03, name='portfolio-03'),
    path('portfolio-04', views.portfolio_04, name='portfolio-04'),
]