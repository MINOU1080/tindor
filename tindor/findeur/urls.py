from django.urls import path
from .import views

app_name = "findeur"  # <--- IMPORTANT


urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profil/', views.profil_view, name='profil'),
    path('browse/', views.browse_view, name='browse'),
    path('matches/', views.matches_view, name='matches'),
    path('logout/',views.logout_view, name='logout'),
    path("vote/<int:target_id>/", views.vote_view, name="vote"),

]