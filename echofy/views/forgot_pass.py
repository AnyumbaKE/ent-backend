import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from echofy.models import PasswordResetOTP
from rest_framework.permissions import IsAuthenticated
from ..serializers import PasswordResetOTPSerializer
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings


User = get_user_model()

#For email
def generate_reset_token(email, otp):
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    return s.dumps({'email': email, 'otp': otp}, salt='reset-password')

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        otp = f"{random.randint(100000, 999999)}"
        PasswordResetOTP.objects.create(user=user, otp=otp)
        token = generate_reset_token(email, otp)
        reset_url = f"{settings.FRONTEND_HOST}/reset_password/{token}"

        send_mail(
            subject='Echofy, Reset Your password',
            message=f"Click the link to reset your password: {reset_url}",
            from_email=None,  #
            recipient_list=[email],
        )
        return Response({'sent': True})
    except User.DoesNotExist:
        return Response({'sent': True})  

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_with_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by('-created_at').first()

        if not otp_obj:
            return Response({'reset': False, 'error': 'Invalid OTP'}, status=400)
        if otp_obj.is_expired():
            return Response({'reset': False, 'error': 'OTP expired'}, status=400)

        user.set_password(password)
        user.save()
        otp_obj.delete()
        return Response({'reset': True})

    except User.DoesNotExist:
        return Response({'reset': False, 'error': 'User not found'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_otps_sent(request):
    filters = request.GET.dict()
    
    if 'user' in filters:
        try:
            filters['user'] = User.objects.get(id=filters['user'])
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)

    otps = PasswordResetOTP.objects.filter(**filters).order_by('-created_at')
    serializer = PasswordResetOTPSerializer(otps, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def decode_reset_token(request):
    from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
    token = request.data.get('token')
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        data = s.loads(token, salt='reset-password', max_age=600)  
        return Response({'email': data['email'], 'otp': data['otp']}, status=200)
    except (BadSignature, SignatureExpired):
        return Response({'error': 'Invalid or expired token'}, status=400)
