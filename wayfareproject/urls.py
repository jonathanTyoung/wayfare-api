from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from wayfareapi.views import (
    register_user,
    login_user,
    current_user_view,
    PostViewSet,
    CategoryViewSet,
    TagViewSet,
    ProfileViewSet,
    PhotoViewSet,
    LikeView,
    CommentView,
    BookmarkView
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"posts", PostViewSet, "post")
router.register(r"categories", CategoryViewSet , "category")
router.register(r"tags", TagViewSet, "tag")
router.register(r"profile", ProfileViewSet, "profile")
router.register(r"photos", PhotoViewSet, basename="photo")

# Add social features
router.register(r"likes", LikeView, basename="like")
router.register(r"comments", CommentView, basename="comment")
router.register(r"bookmarks", BookmarkView, basename="bookmark")

urlpatterns = [
    path("", include(router.urls)),
    path("register", register_user),
    path("login", login_user),
    path("current_user", current_user_view),
    path("admin/", admin.site.urls),
]
