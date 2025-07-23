from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Blog
from ..serializers import BlogSerializer
from ..permissions import IsBlogger, IsAdminUserRole
import cloudinary.uploader
from django.shortcuts import get_object_or_404
import re

# Create Blog (Blogger Only)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsBlogger | IsAdminUserRole])
def create_blog(request):
    title = request.data.get('title')
    text = request.data.get('text')
    image_file = request.FILES.get('image')

    image_url = None
    if image_file:
        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get('secure_url')

    blog = Blog.objects.create(
        user=request.user,
        title=title,
        text=text,
        image_url=image_url
    )
    serializer = BlogSerializer(blog)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_blogs(request):
    raw_filters = request.GET.dict()
    filters = {}

    for key, value in raw_filters.items():
        if key == 'user':
            filters['user__username'] = value
        else:
            filters[key] = value

    blogs = Blog.objects.filter(**filters)
    serializer = BlogSerializer(blogs, many=True)
    return Response(serializer.data)



# Update Blog
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_blog(request, pk):
    # Check if user has admin role using custom permission
    is_admin = IsAdminUserRole().has_permission(request, None)

    if is_admin:
        blog = get_object_or_404(Blog, pk=pk)
    else:
        blog = get_object_or_404(Blog, pk=pk, user=request.user)

    # Get fields or use existing values
    title = request.data.get('title', blog.title)
    text = request.data.get('text', blog.text)
    image_file = request.FILES.get('image')

    # Optional: update image via Cloudinary
    if image_file:
        try:
            upload_result = cloudinary.uploader.upload(image_file)
            blog.image_url = upload_result.get('secure_url')
        except Exception as e:
            return Response({'error': 'Image upload failed', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Update fields
    blog.title = title
    blog.text = text
    blog.save()

    serializer = BlogSerializer(blog)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def validate_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    approval_status = request.data.get('approval_status')
    if approval_status not in ['approved', 'rejected']:
        return Response(
            {'error': 'Invalid approval_status. Must be "approved" or "rejected".'},
            status=status.HTTP_400_BAD_REQUEST
        )

    blog.approval_status = approval_status
    blog.save()

    serializer = BlogSerializer(blog)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Delete Blog

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsBlogger | IsAdminUserRole])
def delete_blog(request, pk):
    try:
        blog = Blog.objects.get(pk=pk, user=request.user)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found or permission denied'}, status=404)

    # Optional: delete image from Cloudinary
    if blog.image_url:
        try:
            # Extract the public_id from the URL
            match = re.search(r'/([^/]+)\.(jpg|jpeg|png|webp)$', blog.image_url)
            if match:
                public_id = match.group(1)
                cloudinary.uploader.destroy(public_id)
        except Exception as e:
            # Log or handle error, but don't block deletion
            print("Cloudinary deletion error:", str(e))

    blog.delete()
    return Response({'message': 'Blog deleted successfully'})
