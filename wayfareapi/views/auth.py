from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    if not username or not password:
        return Response({'valid': False, 'message': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    authenticated_user = authenticate(username=username, password=password)
    if authenticated_user is not None:
        token, _ = Token.objects.get_or_create(user=authenticated_user)
        data = {
            'valid': True,
            'token': token.key,
            'user_id': authenticated_user.id,
            'username': authenticated_user.username,
            'first_name': authenticated_user.first_name,
            'last_name': authenticated_user.last_name,
            'email': authenticated_user.email
        }
        return Response(data)
    return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    email = request.data.get('email', '').strip()
    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()

    if not username or not password:
        return Response({'message': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
    except IntegrityError:
        return Response({'message': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    token = Token.objects.create(user=new_user)
    data = {
        'token': token.key,
        'user_id': new_user.id,
        'username': new_user.username,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'email': new_user.email
    }
    return Response(data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
