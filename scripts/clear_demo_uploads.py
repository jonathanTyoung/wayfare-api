import cloudinary.api
import cloudinary.uploader
import cloudinary
import django
import os
import sys
from dotenv import load_dotenv  # 👈 add this

# ✅ Load .env so your Cloudinary creds are available
load_dotenv()

# ✅ Configure Cloudinary using env vars
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# ✅ Setup Django so we can access models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wayfareproject.settings")
django.setup()

from wayfareapi.models import Photo  # import AFTER django.setup()


def clear_demo_uploads():
    print("🔎 Fetching demo uploads...")

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
