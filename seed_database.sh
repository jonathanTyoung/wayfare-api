#!/bin/bash

# --- Remove old database and migrations ---
echo "Removing old database and migrations..."
rm -f db.sqlite3
rm -rf ./wayfareapi/migrations

# --- Run initial migrations ---
echo "Running initial migrations..."
python3 manage.py migrate
python3 manage.py makemigrations wayfareapi
python3 manage.py migrate wayfareapi

# --- Load fixtures ---
echo "Loading fixtures..."
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata travelers
python3 manage.py loaddata categories
python3 manage.py loaddata tags
python3 manage.py loaddata posts
python3 manage.py loaddata posttags
python3 manage.py loaddata photos
python3 manage.py loaddata likes
python3 manage.py loaddata comments
python3 manage.py loaddata bookmarks

# # --- Seed photos ---
# echo "Seeding placeholder photos into Cloudinary..."
# python3 scripts/seed_photos_cloudinary.py

echo "Database seeding complete!"
