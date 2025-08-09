from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Post


class Posts(ViewSet):
    """Post ViewSet"""

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

    def create(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            post.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)



class PostSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Post
        fields = ( 'id', 'title', 'short_description', "created_at", "category")

