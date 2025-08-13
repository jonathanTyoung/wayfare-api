from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from wayfareapi.models import Post, Tag, Traveler, Category, PostTag
from .travelerViewSet import TravelerSerializer
from .categoryViewSet import CategorySerializer
from .tagViewSet import TagSerializer

class PostSerializer(serializers.ModelSerializer):
    traveler = TravelerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source='category', required=True
    )
    tags = TagSerializer(many=True, read_only=True)
    # tags = serializers.ListField(
    #     child=serializers.CharField(), write_only=True, required=False
    # )

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'short_description',
            'created_at',
            'updated_at',
            'category',
            'category_id',
            'traveler',
            'location_name',
            'tags',
        )


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().prefetch_related(
        Prefetch('tags', queryset=Tag.objects.all())
    )
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("You must be logged in")
        traveler = Traveler.objects.get(user=user)
        post = serializer.save(traveler=traveler)

        tags = self.request.data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        for name in tags:
            tag, _ = Tag.objects.get_or_create(name=name)
            PostTag.objects.get_or_create(post=post, tag=tag)

    def list(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, partial=False):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        tags = request.data.get("tags", None)
        if tags is not None and isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        data = request.data.copy()
        data.pop("tags", None)  # Remove tags before serializer validation

        serializer = PostSerializer(post, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()

            if tags is not None:
                post.tags.clear()
                for name in tags:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    PostTag.objects.get_or_create(post=post, tag=tag)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk, partial=True)

    def destroy(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
