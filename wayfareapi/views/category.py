from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wayfareapi.models import Category


class Categories(ViewSet):
    """Category ViewSet"""

    def list(self, request):
        # Remove the order_by('-created_at') since Category model doesn't have created_at field
        categories = Category.objects.all().order_by('name')  # Order by name instead
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


class CategorySerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Category
        fields = ('id', 'name')