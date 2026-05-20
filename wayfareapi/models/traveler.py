from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Traveler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # def __str__(self):
    #     return self.user.username


@receiver(post_save, sender=User)
def create_traveler_for_user(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    if created:
        Traveler.objects.create(user=instance)
