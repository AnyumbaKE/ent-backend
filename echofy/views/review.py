from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..permissions import IsAdminUserRole
from ..models import ReviewModel
from ..serializers import ReviewSerializer

from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

from ..models import ReviewModel
from ..serializers import ReviewSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    serializer = ReviewSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        sender = request.user
        receiver = serializer.validated_data.get('receiver')
        title = serializer.validated_data.get('title')
        text = serializer.validated_data.get('text')

        subject = f"New Review from {sender.username}: {title}"
        message = f"""
You have received a new review.

Title: {title}

Message:
{text}

Review by: {sender.username} ({sender.email})
"""

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [receiver.email],  # ✅ sent to receiver's email
                fail_silently=False,
            )
        except BadHeaderError:
            return Response({'error': 'Invalid email header.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save only after email is successfully sent
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reviews(request):
    filters = request.GET.dict() 
    reviews = ReviewModel.objects.filter(**filters)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_review(request, pk):
    review = get_object_or_404(ReviewModel, pk=pk)

    # Optional: prevent others from editing your reviews
    if review.sender != request.user:
        return Response({'error': 'Not allowed to edit this review.'}, status=status.HTTP_403_FORBIDDEN)

    partial = request.method == 'PATCH'
    serializer = ReviewSerializer(review, data=request.data, context={'request': request}, partial=partial)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    review = get_object_or_404(ReviewModel, pk=pk)

    # Optional: prevent others from deleting your reviews
    if review.sender != request.user:
        return Response({'error': 'Not allowed to delete this review.'}, status=status.HTTP_403_FORBIDDEN)

    review.delete()
    return Response({'message': 'Review deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
