from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from .auth import UserSerializer
from wayfareapi.models import Traveler


class TravelerViewSet(ViewSet):
    """Traveler view set"""


    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        traveler = Traveler()
        traveler.sample_name = request.data["name"]
        traveler.sample_description = request.data["description"]

        try:
            traveler.save()
            serializer = TravelerSerializer(traveler)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            traveler = Traveler.objects.get(pk=pk)
            serializer = TravelerSerializer(traveler)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            traveler = Traveler.objects.get(pk=pk)
            traveler.sample_name = request.data["name"]
            traveler.sample_description = request.data["description"]
            traveler.save()
        except Traveler.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            traveler = Traveler.objects.get(pk=pk)
            traveler.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Traveler.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            travelers = Traveler.objects.all()
            serializer = TravelerSerializer(travelers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class TravelerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Traveler
        fields = ('id', 'name')  # Only expose ID and full name

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()