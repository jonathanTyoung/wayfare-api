from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db import models
from .traveler import Traveler
from .category import Category

latitude = models.DecimalField(
    max_digits=9, decimal_places=6,
    null=True, blank=True,
    validators=[MinValueValidator(-90), MaxValueValidator(90)]
)
longitude = models.DecimalField(
    max_digits=9, decimal_places=6,
    null=True, blank=True,
    validators=[MinValueValidator(-180), MaxValueValidator(180)]
)

class Post(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name="posts")
    trip = models.ForeignKey('Trip', on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag', through='PostTag', related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(blank=True)
    long_form_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)