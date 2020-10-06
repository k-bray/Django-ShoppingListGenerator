"""shoppinglist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from shoplist import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

     # Auth
    path('signup/', views.signupuser, name='signupuser'),
    path('login/', views.loginuser, name='loginuser'),
    path('logout/', views.logoutuser, name='logoutuser'),

    # Functionality
    path('generate/', views.generate, name='generate'),
    path('addmeal/', views.addmeal, name='addmeal'),
    path('samplemeals/', views.samplemeals, name='samplemeals'),
    path('meal/<int:meal_pk>', views.viewmeal, name='viewmeal'),
    path('editmeal/<int:meal_pk>', views.editmeal, name='editmeal'),
    path('addtomenu/<int:meal_pk>', views.addtomenu, name='addtomenu'),
    path('removefrommenu/<int:meal_pk>', views.removefrommenu, name='removefrommenu'),
    path('mylists/', views.mylists, name='mylists'),
    path('newshoppinglist/', views.newshoppinglist, name='newshoppinglist'),
    path('mylist/<int:list_pk>', views.mylist, name='mylist'),
]
