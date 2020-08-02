from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# Models
from .models import Category 
# Serializers
from .serializers import CategorySerializer

class CategoryViewSet(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CategorySerializer


    def get_queryset(self):
        return Category.objects.all()
'''
params:
    title,
    kwargs,
    description,
    image,
    parent,
    status,
    slug

functions: Retrieve, Delete, Create
'''
class CategoryDetailViewSet(viewsets.ModelViewSet):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CategorySerializer

    def get_serializer(self, *args, **kwargs):

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()

        return serializer_class(*args, **kwargs)

    def get_queryset(self, slug):

        try:
            return Category.objects.get(slug = slug)
        except ObjectDoesNotExist:
            return None
    
    def retrieve(self, request, pk=None):

        instance = self.get_queryset(pk)
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, *args, **kwargs):
  
        instance = self.get_queryset(self.kwargs.get('pk'))
        if instance:
            self.perform_destroy(instance)
            return Response(status = status.HTTP_200_OK)
        return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
    
    def perform_update(self,serializer):
        instance = self.get_queryset(self.kwargs.get('pk'))

        instance.title = serializer.data.get('title')
        instance.description = serializer.data.get('description')
        instance.keywords = serializer.data.get('keywords')
        instance.image = serializer.data.get('image')
        instance.parent__id = serializer.data.get('parent')
        instance.status = serializer.data.get('status')
        instance.slug = serializer.data.get('slug')
        instance.updated_at = timezone.now()
        instance.save()
        
    def update(self, request, *args, **kwargs):
              
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        
        return Response(serializer.data, status = status.HTTP_200_OK)
        



