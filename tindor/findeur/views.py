from math import radians, sin, cos, sqrt, atan2
from profile import Profile

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Vote


def _distance_km(lat1, lon1, lat2, lon2):
    """Retourne la distance en kilomètres entre deux points (lat, lon)."""
    R = 6371.0  # rayon moyen de la Terre (km)
    lat1_r, lon1_r, lat2_r, lon2_r = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2_r - lon1_r
    dlat = lat2_r - lat1_r

    a = sin(dlat/2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon/2)**2

    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def _parse_coords(s: str):
    # attend "50.85, 4.35" -> (50.85, 4.35)
    try:
        lat_str, lon_str = s.split(",")
        return float(lat_str.strip()), float(lon_str.strip())
    except Exception:
        return None, None


def _candidates_for(user):
    """
    Retourne les profils compatibles selon l'intérêt,
    non encore votés et situés à moins de 5 km.
    """
    my_profile = user.profile
    print("👤 Utilisateur courant:", user.username, my_profile.genre, my_profile.interet)

    my_lat, my_lon = my_profile.latitude, my_profile.longitude
    print("📍 Coordonnées:", my_lat, my_lon)

    voted_user_ids = Vote.objects.filter(voter=user).values_list("target_id", flat=True)
    print("🗳️ Déjà voté:", list(voted_user_ids))

    qs = Profile.objects.exclude(user=user).exclude(user__id__in=voted_user_ids)
    if my_profile.interet != "peu_importe":
        qs = qs.filter(genre=my_profile.interet)
    print("🎯 Après filtre intérêt:", [p.user.username for p in qs])

    # filtre distance
    if my_lat is not None and my_lon is not None:
        nearby = []
        print(my_lat)
        print(my_lon)
        print(user.username)
        for p in qs:
            if p.latitude is not None and p.longitude is not None:
                print(p.user.username)
                print(p.latitude)
                print(p.longitude)
                dist = _distance_km(my_lat, my_lon, p.latitude, p.longitude)
                print(dist)
                if dist <= 500:
                    nearby.append(p.user.id)

        qs = qs.filter(user__id__in=nearby)
        print("📍 À moins de 5km:", [p.user.username for p in qs])


    print("✅ Résultat final:", [p.user.username for p in qs])
    return qs.select_related("user")



def home(request):
    return render(request,'findeur/home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('findeur:browse')  # page après login
        return render(request, "findeur/login.html", {"error": "Identifiants invalides."})

    return render(request, "findeur/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("password")
        genre = request.POST.get("genre")
        interet = request.POST.get("interet")
        coordonnees = request.POST.get("coordonnees")

        print(f"{username} s’est inscrit ({genre}, {interet}, {coordonnees})")

        # validations simples
        if not username or not password:
            return render(request, "findeur/register.html", {"error": "Identifiant et mot de passe requis."})
        if User.objects.filter(username=username).exists():
            return render(request, "findeur/register.html", {"error": "Cet identifiant existe déjà."})

        lat, lon = _parse_coords(coordonnees)

        # crée l'utilisateur (hash auto du mot de passe)
        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, genre=genre, interet=interet, latitude=lat, longitude=lon)

        # connecte directement l’utilisateur
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('findeur:browse')  # ou 'findeur:matches' selon ton flux

        return render(request, "findeur/register.html", {"error": "Impossible de connecter l'utilisateur."})


    return render(request, 'findeur/register.html')

@login_required
def matches_view(request):
    # ids des users pour lesquels current user a mis like
    liked_ids = Vote.objects.filter(voter=request.user, value=1).values_list("target_id", flat=True)

    # ids des users qui ont aimé current user
    liked_by_ids = Vote.objects.filter(target=request.user, value=1).values_list("voter_id", flat=True)

    # intersection -> ids mutuels
    mutual_ids = set(liked_ids).intersection(set(liked_by_ids))

    matches = User.objects.filter(id__in=mutual_ids).select_related("profile")

    return render(request, "findeur/matches.html", {"matches": matches})

@login_required
def browse_view(request):
    candidates = _candidates_for(request.user)
    next_profile = candidates.first()  # None si vide

    return render(request, "findeur/browse.html", {
        "profile": next_profile
    })

@login_required
def profil_view(request):
    p = request.user.profile  # profil de l'utilisateur connecté

    if request.method == "POST":
        p.genre = request.POST.get("genre", p.genre)
        p.interet = request.POST.get("interet", p.interet)
        p.save()
        # Optionnel: message de succès via django.contrib.messages
        return redirect('findeur:profil')  # recharge la page (PRG pattern)

    # GET : afficher le formulaire pré-rempli
    return render(request, "findeur/profile.html", {"profile": p})

@login_required
def vote_view(request, target_id):
    if request.method != "POST":
        return redirect('findeur:browse')

    value = int(request.POST.get("value", 0))
    target_user = get_object_or_404(User, id=target_id)

    # 🛑 éviter de voter sur soi-même
    if target_user == request.user:
        return redirect('findeur:browse')

    # ✅ Crée ou met à jour le vote
    try:
        Vote.objects.create(voter=request.user, target=target_user, value=value)
    except IntegrityError:
        Vote.objects.filter(voter=request.user, target=target_user).update(value=value)

    # 💞 Si c’est un "like" (=1), vérifier la réciprocité
    if value == 1:
        reciprocal = Vote.objects.filter(
            voter=target_user,
            target=request.user,
            value=1
        ).exists()

        if reciprocal:
            messages.success(request, f"🎉 C’est un match avec {target_user.username} ! 💘")

    # 🔁 Retour à la page de découverte
    return redirect('findeur:browse')

def logout_view(request):
    logout(request)
    return redirect('findeur:home')