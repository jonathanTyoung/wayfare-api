# raterapi/views/user_view.py (or add to existing views.py)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wayfareapi.models import Traveler
# raterapi/serializers/user_serializer.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

User = get_user_model()

# serializers.py
class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = ['id', 'user']  # your traveler fields

class UserSerializer(serializers.ModelSerializer):
    traveler = TravelerSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'traveler']
