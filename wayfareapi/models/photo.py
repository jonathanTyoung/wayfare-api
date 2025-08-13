from django.db import models
from .post import Post

class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="photos")
    image_url = models.URLField()
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.post.title}"
