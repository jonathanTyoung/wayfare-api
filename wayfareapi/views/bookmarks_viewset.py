from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Bookmark


class BookmarkView(ViewSet):
    """Bookmark view set"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(traveler__user=self.request.user)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        post_id = request.data.get("post")
        if not post_id:
            return Response({"reason": "post is required"}, status=status.HTTP_400_BAD_REQUEST)

        bookmark, created = Bookmark.objects.get_or_create(
            traveler=request.user.traveler,
            post_id=post_id
        )
        serializer = BookmarkSerializer(bookmark)
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=code)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            bookmark = Bookmark.objects.get(pk=pk)
            serializer = BookmarkSerializer(bookmark)
            return Response(serializer.data)
        except Bookmark.DoesNotExist:
            return Response({"reason": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 204, 403, or 404 status code
        """
        try:
            bookmark = Bookmark.objects.get(pk=pk)
        except Bookmark.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if bookmark.traveler.user != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        bookmark.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        queryset = self.get_queryset()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = BookmarkSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BookmarkSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Bookmark
        fields = ('id', 'traveler', 'post', 'created_at')