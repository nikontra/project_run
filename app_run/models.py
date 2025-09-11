from email.policy import default

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Run(models.Model):
    STATUS_CHOICES = [
        ("init", "Забег инициализирован"),
        ("in_progress", "Забег начат"),
        ("finished", "Забег закончен")
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="init")
