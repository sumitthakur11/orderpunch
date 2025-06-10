"""
URL configuration for Bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Tradingbot import views

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/csrf_token',views.get_csrf_token,name= "token"),

    path('api/login',views.LoginAPI.as_view(),name='login'),
    path('api/broker', views.broker.as_view(), name="broker"),
    path('api/placeorder', views.placeorder.as_view(), name="placeholder"),
    path('api/symbols', views.Getsymbols.as_view(), name="symbol"),
    path('api/loginbroker', views.loginbroker.as_view(), name="loginbroker"),
    path('api/loginredirect', views.loginbrokerredirect.as_view(), name="loginbroker"),

    
    path('api/logoutbroker', views.logoutbroker.as_view(), name="logoutbroker"),
    path('api/position', views.postionsobj.as_view(), name="logoutbroker"),
    path('api/watchlist', views.watchlist.as_view(), name="logoutbroker"),
    path('api/loadaccount', views.loadaccount.as_view(), name="logoutbroker"),
    path('api/sendlog', views.sendlog.as_view(), name="sendlog"),
    path('api/getfunds', views.getfunds.as_view(), name="getfunds"),
    path('api/getposition', views.getposition.as_view(), name="getposition"),
    path('api/getholding', views.getholding.as_view(), name="getholding"),




    


    
    




]
