from django.db import models
from django.contrib.auth.models import User



class Run(models.Model):
    STATUS_CHOICES = [
        ("init", "Забег инициализирован"),
        ("in_progress", "Забег начат"),
        ("finished", "Забег закончен")
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="runs")
    comment = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="init")


class AthleteInfo(models.Model):
    weight = models.IntegerField(null=True, blank=True)
    goals = models.CharField(max_length=200)
    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="athlete_info"
    )

class Challenge(models.Model):
    full_name = models.CharField(max_length=50)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenges")
