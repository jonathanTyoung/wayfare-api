from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Prefetch
from wayfareapi.models import Post, Tag, Traveler, Category, PostTag
from .travelerViewSet import TravelerSerializer
from .categoryViewSet import CategorySerializer
from .tagViewSet import TagSerializer


# ---------------------------
# Serializer
# ---------------------------
class PostSerializer(serializers.ModelSerializer):
    traveler = TravelerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source='category', required=True
    )
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'latitude', 'longitude', 'short_description',
            'created_at', 'updated_at', 'category', 'category_id',
            'traveler', 'location_name', 'tags'
        )


# ---------------------------
# ViewSet
# ---------------------------
class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all().prefetch_related(Prefetch('tags', queryset=Tag.objects.all()))

    # -----------------------
    # CREATE
    # -----------------------
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("You must be logged in")

        traveler = Traveler.objects.get(user=user)
        post = serializer.save(traveler=traveler)
        self._handle_tags(post, self.request.data.get("tags", []))

    # -----------------------
    # TAG HANDLER
    # -----------------------
    def _handle_tags(self, post: Post, tags_input):
        """
        Normalize tags and link to post
        """
        if isinstance(tags_input, str):
            tags_input = [t.strip() for t in tags_input.split(",") if t.strip()]

        for name in tags_input:
            normalized_name = name.lower()
            tag, _ = Tag.objects.get_or_create(name=normalized_name)
            PostTag.objects.get_or_create(post=post, tag=tag)

    # -----------------------
    # LIST WITH FILTERS
    # -----------------------
    def list(self, request):
        """
        GET /posts/?search=&category=&traveler=
        Filters posts by:
        - search: title, short_description, category name, traveler name, tag name
        - category: category name
        - traveler: traveler name
        """
        queryset = Post.objects.all().order_by('-updated_at')
        search = request.query_params.get("search", "").strip()
        category = request.query_params.get("category", "").strip()
        traveler = request.query_params.get("traveler", "").strip()

        # Filter by search term
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(traveler__traveler__icontains=search) |
                Q(tags__name__icontains=search)  # new: search by tag name
            ).distinct()  # distinct to prevent duplicates from multiple tag matches

        # Optional filters
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        if traveler:
            queryset = queryset.filter(traveler__traveler__iexact=traveler)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    # -----------------------
    # POSTS BY TRAVELER
    # -----------------------
    @action(detail=False, methods=["get"], url_path="traveler/(?P<traveler_id>[^/.]+)")
    def posts_by_traveler(self, request, traveler_id=None):
        posts = Post.objects.filter(traveler_id=traveler_id).order_by('-updated_at')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # -----------------------
    # RETRIEVE
    # -----------------------
    def retrieve(self, request, pk=None):
        post = self.get_object_or_404(pk)
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    # -----------------------
    # UPDATE / PARTIAL UPDATE
    # -----------------------
    def update(self, request, pk=None, partial=False):
        post = self.get_object_or_404(pk)
        tags = request.data.pop("tags", None)

        serializer = self.get_serializer(post, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if tags is not None:
            post.tags.clear()
            self._handle_tags(post, tags)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        return self.update(request, pk, partial=True)

    # -----------------------
    # DELETE
    # -----------------------
    def destroy(self, request, pk=None):
        post = self.get_object_or_404(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # -----------------------
    # HELPER
    # -----------------------
    def get_object_or_404(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
