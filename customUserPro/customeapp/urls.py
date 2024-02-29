from django.urls import path
from .views import fetchData, manageUser,useraccountActivate,user_create

urlpatterns = [
    path('create/', user_create),
    path('fetch/', fetchData),
    path('details/<int:pk>/', manageUser),
    path('activate/<uid>/<token>/',useraccountActivate, name='activate')
]
