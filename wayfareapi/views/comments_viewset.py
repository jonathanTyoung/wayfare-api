from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Comment


class CommentView(ViewSet):
    """Comment view set"""

    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        post_id = request.data.get("post")
        content = request.data.get("content", "").strip()
        if not post_id or not content:
            return Response({"reason": "post and content are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = Comment()
            comment.traveler = request.user.traveler
            comment.post_id = post_id
            comment.content = content
            comment.save()
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Comment.DoesNotExist:
            return Response({"reason": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            comment = Comment.objects.get(pk=pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({"reason": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """Handle PUT requests — only the comment owner may edit content

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if comment.traveler.user != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        content = request.data.get("content", "").strip()
        if not content:
            return Response({"reason": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

        comment.content = content
        comment.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 204, 403, or 404 status code
        """
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if comment.traveler.user != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Comment
        fields = ('id', 'traveler', 'post', 'content', 'created_at', 'updated_at')