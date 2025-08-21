from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
import cloudinary.uploader
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Prefetch
from wayfareapi.models import Post, Tag, Traveler, Category, PostTag, Photo, Comment, Like
from .travelers_viewset import TravelerSerializer
from .categories_viewset import CategorySerializer
from .tags_viewset import TagSerializer
from .photos_viewset import PhotoSerializer
from .likes_viewset import LikeSerializer


# ---------------------------
# Serializer
# ---------------------------
class CommentSerializer(serializers.ModelSerializer):
    traveler = TravelerSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "traveler", "content", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    traveler = TravelerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category',
        required=True
    )
    tags = TagSerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    # Social features
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    liked_by_user = serializers.SerializerMethodField()
    bookmarks_count = serializers.IntegerField(source="bookmarks.count", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    # First photo thumbnail
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'latitude', 'longitude', 'short_description', 'long_form_description',
            'created_at', 'updated_at', 'category', 'category_id',
            'traveler', 'location_name', 'tags', 'photos',
            'likes_count', 'liked_by_user', 'bookmarks_count', 'comments', 'thumbnail'
        )

    def get_thumbnail(self, obj):
        first_photo = obj.photos.first()
        return first_photo.url if first_photo else None
    
    def get_liked_by_user(self, obj):
        user = self.context['request'].user
        if not hasattr(user, 'traveler'):
            return False
        return obj.likes.filter(traveler=user.traveler).exists()


# -----------------------
# ViewSet
# -----------------------
class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all().prefetch_related(
        Prefetch('tags', queryset=Tag.objects.all()),
        Prefetch('photos', queryset=Photo.objects.all()),
        Prefetch('likes', queryset=Like.objects.all())
    )
    @action(detail=False, url_path='traveler/(?P<traveler_id>[^/.]+)')
    def by_traveler(self, request, traveler_id=None):
        posts = self.queryset.filter(traveler__id=traveler_id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
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
    # UPLOAD PHOTO
    # -----------------------
    @action(detail=True, methods=["post"])
    def upload_photo(self, request, pk=None):
        post = self.get_object()
        image_file = request.FILES.get("file")
        if not image_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        upload_result = cloudinary.uploader.upload(
            image_file,
            folder="demo_uploads",
            tags=["demo"]
        )

        photo = Photo.objects.create(
            post=post,
            url=upload_result["secure_url"],
            public_id=upload_result["public_id"]
        )

        return Response({"url": photo.url, "id": photo.id}, status=status.HTTP_201_CREATED)

    # -----------------------
    # LIKE / UNLIKE
    # -----------------------
    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        traveler = request.user.traveler

        if request.method == "POST":
            like, created = Like.objects.get_or_create(post=post, traveler=traveler)
            if created:
                return Response({"status": "liked"}, status=status.HTTP_201_CREATED)
            return Response({"status": "already liked"}, status=status.HTTP_200_OK)

        deleted, _ = Like.objects.filter(post=post, traveler=traveler).delete()
        if deleted:
            return Response({"status": "unliked"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "not liked"}, status=status.HTTP_400_BAD_REQUEST)

    # -----------------------
    # TAG HANDLER
    # -----------------------
    def _handle_tags(self, post: Post, tags_input):
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
        queryset = Post.objects.all().prefetch_related(
            'tags', 'photos', 'likes'
        ).order_by('-updated_at')

        search = request.query_params.get("search", "").strip()
        category = request.query_params.get("category", "").strip()
        traveler = request.query_params.get("traveler", "").strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(traveler__name__icontains=search) |
                Q(traveler__username__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        if category:
            queryset = queryset.filter(category__name__iexact=category)
        if traveler:
            queryset = queryset.filter(
                Q(traveler__name__iexact=traveler) |
                Q(traveler__username__iexact=traveler)
            )

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)