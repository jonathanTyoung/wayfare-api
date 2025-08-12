from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from wayfareapi.models import Post, Tag, Traveler, Category
from .travelerViewSet import TravelerSerializer
from .categoryViewSet import CategorySerializer
from .tagViewSet import TagSerializer

class PostSerializer(serializers.ModelSerializer):
    traveler = TravelerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source='category', required=True
    )
    tags = TagSerializer(many=True)

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
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        print(f"Current user: {user}")  # or log it
        if user.is_anonymous:
            raise PermissionDenied("You must be logged in")
        # Link the post to the currently authenticated traveler
        traveler = Traveler.objects.get(user=self.request.user)
        post = serializer.save(traveler=traveler)

        # Handle tags: accept array of strings from request
        tag_names = self.request.data.get("tags", [])
        if isinstance(tag_names, str):  # Handle if tags come as comma-separated string
            tag_names = [t.strip() for t in tag_names.split(",") if t.strip()]

        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name.strip())
            post.tags.add(tag)




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


    # def create(self, request):
    #     tags_data = request.data.pop("tags", []) #pop extracts the tags from the payload that is sent
    #     data = request.data.copy()
    #     data['traveler'] = request.user.traveler.id

    #     serializer = PostSerializer(data=request.data)
    #     if serializer.is_valid():
    #         post = serializer.save()  # create post instance

    #         # Handle tags
    #         for tag_name in tags_data:
    #             tag, created = Tag.objects.get_or_create(name=tag_name)
    #             PostTag.objects.get_or_create(post=post, tag=tag)

    #         # Re-serialize post including tags for response
    #         response_serializer = PostSerializer(post)
    #         return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None, partial=False):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        # Extract tags from request data
        tag_names = request.data.get("tags", None)
        if tag_names is not None and isinstance(tag_names, str):
            tag_names = [t.strip() for t in tag_names.split(",") if t.strip()]

        # Remove tags from data before passing to serializer
        data = request.data.copy()
        if "tags" in data:
            data.pop("tags")

        serializer = PostSerializer(post, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()

            # Update tags after saving post
            if tag_names is not None:
                post.tags.clear()
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def partial_update(self, request, pk=None):
    #     # Call update with partial=True for PATCH requests
    #     return self.update(request, pk, partial=True)

    def destroy(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            post.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)





