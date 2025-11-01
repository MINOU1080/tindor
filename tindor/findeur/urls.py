from django.urls import path
from .views import home
from ..tindor.urls import urlpatterns

urlpatterns = [
    path('',home, name='home'),
]