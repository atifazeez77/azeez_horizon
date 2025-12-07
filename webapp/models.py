from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    target_score = models.IntegerField(default=90)
    library_hours = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.username