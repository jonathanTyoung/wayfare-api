from django.db import models 
from .traveler import Traveler
from .post import Post


class Bookmark(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name="bookmarks")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("traveler", "post")