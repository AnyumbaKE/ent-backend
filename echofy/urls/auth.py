from django.urls import path
from echofy.views import CustomRefreshToken, CustomTokenObtainPairView, is_authenticated, get_all_users, logout
from echofy.views import register_user
from echofy.views import forgot_password, reset_password_with_otp, decode_reset_token


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshToken.as_view(), name='token_refresh'),
    path('authenticated/', is_authenticated),
    path('register/', register_user),
    path('users/', get_all_users, name='get-all-users'),
    path('forgot-password/', forgot_password),
    path('reset-password/', reset_password_with_otp),
    path('decode-reset-token/', decode_reset_token),
    path('logout/', logout, name='logout'),

]
