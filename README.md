
# 🌍 Wayfare  
*A geotagged storytelling platform built with Django REST Framework and React.*

## 📖 Overview
**Wayfare** lets users share experiences tied to real-world locations.  
Each post can include a title, description, photos, and a geotag that displays as an interactive pin on a world map.  
It’s designed to blend journaling, travel blogging, and social discovery into one visual experience.

Users can:
- Create, edit, and delete their own posts with photos and descriptions.
- Explore experiences pinned to the map.
- Like and bookmark other users’ posts.
- View their profile and all their created posts.
- Interact with posts through an image carousel and responsive UI.

---

## 🎥 Demo Walkthrough
Take a quick look at Wayfare in action — a **3min demo video** showcasing user registration, post creation, the interactive map, likes/bookmarks, and profile management.  Recommend watching at 1.2x speed
▶️ [Watch on Loom](https://www.loom.com/share/710ccbb6ebc84951ba08ce1465bf0cac)

---

## ⚙️ Tech Stack
**Frontend:** React, Vite, SCSS, Axios  
**Backend:** Django REST Framework, Cloudinary (for image storage)  
**Authentication:** Django Token Authentication  
**Mapping:** React Leaflet  
**Other Tools:**  
- Debounced search functionality for smoother input performance  
- RESTful API endpoints for posts, comments, likes, and bookmarks  
- Modular component-based design for scalability  

---

## 🚀 Getting Started

### 1️⃣ Clone the Repositories
Wayfare is organized into two separate repos:
- **Client (frontend):** [wayfare-client](https://github.com/jonathanTyoung/wayfare-client)
- **API (backend):** [wayfare-api](https://github.com/jonathanTyoung/wayfare-api)

Clone both into your workspace:
```bash
git clone https://github.com/jonathanTyoung/wayfare-client.git
git clone https://github.com/jonathanTyoung/wayfare-api.git
