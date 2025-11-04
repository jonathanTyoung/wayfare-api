from django.db import models
from .traveler import Traveler
from .post import Post

class Comment(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)