from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Traveler


class TravelerViewSet(ViewSet):
    """Traveler view set"""

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            traveler = Traveler.objects.get(pk=pk)
            serializer = TravelerSerializer(traveler)
            return Response(serializer.data)
        except Traveler.DoesNotExist:
            return Response({"reason": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """Handle PUT requests — only the profile owner may update

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            traveler = Traveler.objects.get(pk=pk)
        except Traveler.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if traveler.user != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        traveler.bio = request.data.get("bio", traveler.bio)
        traveler.profile_image = request.data.get("profile_image", traveler.profile_image)
        traveler.location = request.data.get("location", traveler.location)
        traveler.website = request.data.get("website", traveler.website)
        traveler.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 204, 403, or 404 status code
        """
        try:
            traveler = Traveler.objects.get(pk=pk)
        except Traveler.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if traveler.user != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        traveler.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        travelers = Traveler.objects.all()
        serializer = TravelerSerializer(travelers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TravelerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)


    class Meta:
        model = Traveler
        fields = ('id', 'name', 'username')

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()