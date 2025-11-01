from django.db import models

# Create your models here.

from django.db import models


class User(models.Model):
    id = models.CharField(max_length=128)
    password = models.CharField(max_length=128)

    GENRE_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
        ('O', 'Autre'),
    ]
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)

    INTEREST_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
        ('O', 'Autre'),
    ]
    interest = models.CharField(max_length=1, choices=INTEREST_CHOICES)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return (f"Utilsateur  {self.id}"
                f"Genre {self.genre}"
                f"Interest {self.interest}"
                f"Lieu ({self.latitude}, {self.longitude})")