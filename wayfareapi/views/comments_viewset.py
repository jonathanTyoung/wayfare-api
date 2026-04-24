from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Comment, Traveler


class TravelerBriefSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Traveler
        fields = ('id', 'username')


class ReplySerializer(serializers.ModelSerializer):
    traveler = TravelerBriefSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'traveler', 'content', 'created_at')


class CommentSerializer(serializers.ModelSerializer):
    traveler = TravelerBriefSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ('id', 'traveler', 'post', 'content', 'created_at', 'updated_at', 'replies', 'parent_id')


class CommentView(ViewSet):
    """Comment view set"""

    permission_classes = [IsAuthenticated]

    def create(self, request):
        post_id = request.data.get("post")
        content = request.data.get("content", "").strip()
        parent_id = request.data.get("parent_id")

        if not post_id or not content:
            return Response({"reason": "post and content are required"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment()
        comment.traveler = request.user.traveler
        comment.post_id = post_id
        comment.content = content
        if parent_id:
            comment.parent_id = parent_id
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({"reason": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
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
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if comment.traveler.user != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        post_id = request.query_params.get("post_id")
        comments = Comment.objects.filter(parent__isnull=True).prefetch_related('replies__traveler__user')
        if post_id:
            comments = comments.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
