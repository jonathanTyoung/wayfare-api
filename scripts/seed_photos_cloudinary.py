#!/usr/bin/env python3
from random import choice
import os
import sys
import django
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Setup Django environment ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wayfareproject.settings")
django.setup()

from wayfareapi.models import Photo, Post

# --- Configure Cloudinary ---
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# --- Settings ---
NUM_IMAGES_PER_POST = 3
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600

# --- Generate and upload images ---
for post in Post.objects.all():
    if post.photos.exists():
        # Skip posts that already have photos
        print(f"⏭ Skipping post {post.id}, photos already exist")
        continue

    for i in range(NUM_IMAGES_PER_POST):
        # Generate a unique Picsum URL per image
        picsum_url = f"https://picsum.photos/seed/{post.id}-{i}/{IMAGE_WIDTH}/{IMAGE_HEIGHT}"

        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(picsum_url)
            cloud_url = result["secure_url"]

            # Create Photo object in DB
            Photo.objects.create(
                post=post,
                url=cloud_url,
            )
            print(f"✅ Uploaded {cloud_url} for post {post.id}")

        except Exception as e:
            print(f"❌ Failed to upload image for post {post.id}: {e}")

print("🌄 Finished seeding photos!")
