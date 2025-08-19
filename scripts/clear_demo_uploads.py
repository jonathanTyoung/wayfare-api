# scripts/clear_demo_uploads.py
import cloudinary.api
import cloudinary.uploader
import django
import os
import sys
from wayfareapi.models import Photo  # adjust if your Photo model lives elsewhere

# ✅ Setup Django so we can access models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wayfare.settings")  # adjust if needed
django.setup()



def clear_demo_uploads():
    print("🔎 Fetching demo uploads...")

    # 1) Query Cloudinary for all resources tagged "demo"
    resources = cloudinary.api.resources_by_tag("demo")

    count = 0
    for res in resources.get("resources", []):
        public_id = res["public_id"]
        print(f"🗑 Deleting {public_id} from Cloudinary...")
        cloudinary.uploader.destroy(public_id)
        count += 1

        # 2) Also delete from local DB if we stored it
        Photo.objects.filter(public_id=public_id).delete()

    print(f"✅ Deleted {count} demo uploads.")


if __name__ == "__main__":
    clear_demo_uploads()
