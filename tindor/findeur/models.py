from django.contrib.auth.models import User
from django.db import models

# Create your models here.

from django.db import models


class Profile(models.Model):
    GENDER_CHOICES = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
        ('autre', 'Autre'),
    ]
    INTEREST_CHOICES = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
        ('peu_importe', 'Peu importe'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    genre = models.CharField(max_length=12, choices=GENDER_CHOICES)
    interet = models.CharField(max_length=12, choices=INTEREST_CHOICES)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return (f"Utilsateur  {self.user}"
                f"Genre {self.genre}"
                f"Interest {self.interet}"
                f"Lieu ({self.latitude}, {self.longitude})")


class Vote(models.Model):
    VOTE_CHOICES = [
        (1, "like"),
        (0, "dislike"),
    ]

    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes_made")
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes_received")
    value = models.IntegerField(choices=VOTE_CHOICES)  # 1 = like, 0 = dislike
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("voter", "target")  # un vote par paire