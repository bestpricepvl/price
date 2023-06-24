"""price URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from django.conf.urls import include

from django.conf import settings # new
from django.conf.urls.static import static # new

from bestprice import views
from rest_framework import routers
from django.contrib.auth import views as auth_views 

router_prices = routers.SimpleRouter()
router_prices.register(r'prices', views.PricesViewSet)

""" Определение маршрутов """
""" Переменная urlpatterns определяет набор сопоставлений функций обработки с определенными строками запроса.
Например, запрос к корню веб-сайта будет обрабатываться функцией index,
запрос по адресу "about" будет обрабатываться функцией about,
а запрос "contact" - функцией contact. """
urlpatterns = [
    path('', views.index),
    path('index', views.index, name='index'),
    path('duration', views.duration, name='duration'),
    path('create/', views.create, name='create'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),    
    path('json/<action>/', views.json),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('export/excel/', views.export_prices_excel, name='export_prices_excel'),     
    path('export/csv/', views.export_prices_csv, name='export_prices_csv'),

    path('api/drf-auth/', include('rest_framework.urls')),
    path('api/', include(router_prices.urls)),     #http://127.0.0.1:8000/api/prices/, 

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    re_path(r'^register/$', views.register, name='register'),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]



