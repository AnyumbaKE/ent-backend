import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from echofy.models import LoginOTP
from rest_framework.response import Response


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def request_login_otp(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        otp = f"{random.randint(100000, 999999)}"
        LoginOTP.objects.create(user=user, otp=otp)

        send_mail(
            subject='Echofy Login OTP',
            message=f'Your login OTP is {otp}. It expires in 5 minutes.',
            from_email=None,
            recipient_list=[email]
        )
        return Response({'sent': True})
    except User.DoesNotExist:
        return Response({'sent': True})
    

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from echofy.models import LoginOTP

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    try:
        user = User.objects.get(email=email)
        otp_obj = LoginOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj:
            return Response({'login': False, 'error': 'Invalid OTP'}, status=400)
        if otp_obj.is_expired():
            return Response({'login': False, 'error': 'OTP expired'}, status=400)

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Set tokens in cookies
        res = Response(
            {
                "login": True,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            status=status.HTTP_200_OK,
        )

        res.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
        )

        res.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
        )

        return res

    except User.DoesNotExist:
        return Response({'login': False, 'error': 'User not found'}, status=400)