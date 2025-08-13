from django.contrib.auth.models import User
from django.db import models

class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    cover_image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
