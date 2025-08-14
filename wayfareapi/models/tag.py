from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Normalize to lowercase before saving
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        # Capitalized for display purposes
        return self.name.capitalize()
