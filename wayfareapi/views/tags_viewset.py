from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Tag


class TagViewSet(ViewSet):
    """Tag view set"""

    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Handle POST operations"""
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"reason": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

        tag = Tag()
        tag.name = name
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
            return Response({"reason": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """Handle PUT requests"""
        try:
            tag = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get("name", "").strip()
        if not name:
            return Response({"reason": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

        tag.name = name
        try:
            tag.save()
        except Exception as e:
            return Response({"reason": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item"""
        try:
            tag = Tag.objects.get(pk=pk)
            tag.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response({"reason": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests for all items"""
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
