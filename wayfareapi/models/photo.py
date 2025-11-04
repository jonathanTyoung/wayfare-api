from django.db import models
from .post import Post

class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="photos")
    url = models.URLField()
    public_id = models.CharField(max_length=255, blank=True, null=True)  # Add this
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Photo for {self.post.title}"
