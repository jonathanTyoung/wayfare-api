from django.db import models
from .traveler import Traveler

class Like(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey("wayfareapi.Post", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("traveler", "post")
