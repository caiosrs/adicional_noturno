#calculos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calcular/', views.calcular_adicional_noturno, name='calcular_adicional_noturno'),
]