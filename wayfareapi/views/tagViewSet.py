from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Tag


class TagViewSet(ViewSet):
    """Tag view set"""

    def create(self, request):
        """Handle POST operations"""
        tag = Tag()
        tag.name = request.data.get("name")

        try:
            tag.save()
            serializer = TagSerializer(tag)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item"""
        try:
            tag = Tag.objects.get(pk=pk)
            serializer = TagSerializer(tag)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response({'message': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests"""
        try:
            tag = Tag.objects.get(pk=pk)
            tag.name = request.data.get("name")
            tag.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(str(ex))

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item"""
        try:
            tag = Tag.objects.get(pk=pk)
            tag.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist as ex:
            return Response({'message': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items"""
        try:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(str(ex))


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
