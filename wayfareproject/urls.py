from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from wayfareapi.views import (
    register_user,
    login_user,
    current_user_view,
    Posts,
    Categories
    )

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"posts", Posts, "post")
router.register(r"categories", Categories , "category")

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('current_user', current_user_view),
    # path("api-token-auth", obtain_auth_token),
    # path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
]

