from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='cart.index'),
    path('<int:id>/add/', views.add, name='cart.add'),
    path('clear/', views.clear, name='cart.clear'),
    path('<int:id>/edit_quantity/', views.edit_quantity, name='cart.edit_quantity'),
    path('purchase/', views.purchase, name='cart.purchase')
]