from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),
    path('login/', views.login, name='login'),  
    path('logout/', views.logout, name='logout'),
    path('custDashboard/', views.custDashboard, name='custDashboard'),
    path('vendorDashboard/', views.custDashboard, name='vendorDashboard'),
    path('myAccount/', views.myAccount, name='myAccount'),
]