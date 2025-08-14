from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from wayfareapi.models import Traveler

# rewrite serializers for specific fields
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', "name"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = ['id', 'bio', 'profile_image', 'location']

class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    traveler = TravelerSerializer()


# create a profileViewSet to handle displaying Profile datar
class ProfileViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        traveler = getattr(user, 'traveler', None)
        return Response({
            "user": UserSerializer(user).data,
            "traveler": TravelerSerializer(traveler).data if traveler else None
        })