from rest_framework import serializers
from wayfareapi.models import Photo
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated



class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'  # or list fields explicitly



class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
