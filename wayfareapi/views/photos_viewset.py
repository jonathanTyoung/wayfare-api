from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from wayfareapi.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        photo = self.get_object()
        if photo.post.traveler.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own photos.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.post.traveler.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own photos.")
        instance.delete()
