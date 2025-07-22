from django.urls import path
from echofy.views import (
    #Tests
    get_tests, create_test, update_test, delete_test, get_tests_with_audio,

    #Audio
    get_audio_test_base64,

    #Test sessions
    user_test_sessions, start_test_session, get_all_test_sessions, check_test_answer,

    #Blog
     create_blog, list_blogs, update_blog, delete_blog, validate_blog,

     #OTP
    get_otps_sent,

    #REVIEW
    create_review, list_reviews, update_review, delete_review
    )

urlpatterns = [

    path('tests/', get_tests, name='get-tests'),     
    path('tests/audio/', get_tests_with_audio, name='get-tests-with-audio'),        
    path('tests/add/', create_test, name='add-test'),      # Admin only
    path('tests/<int:pk>/update/', update_test, name='update-test'),  # Admin only
    path('tests/<int:pk>/delete/', delete_test, name='delete-test'),  # Admin only

    # New Audio Test Endpoint (base64 audio)
    path('testaudio/base64/', get_audio_test_base64, name='get-audio-test-base64'),

    # Test Sessions
    path('testsession/user/', user_test_sessions, name='user-test-sessions'),  # Authenticated user
    path('testsession/start/', start_test_session, name='start-test-session'),  # Authenticated user
    path('testsession/all/', get_all_test_sessions, name='get-all-test-sessions'),  # Admin only
    path('testsession/check-answer/', check_test_answer, name='check-test-answer'),

    #Blog
    path('blogs/', list_blogs, name='list-blogs'),
    path('blogs/create/', create_blog, name='create-blog'),
    path('blogs/<int:pk>/update/', update_blog, name='update-blog'),
    path('blogs/<int:pk>/validate/', validate_blog, name='validate-blog'),
    path('blogs/<int:pk>/delete/', delete_blog, name='delete-blog'),

    #OTP
    path('otps/', get_otps_sent, name='get_otps_sent'),

    #Review
    path('reviews/', list_reviews, name='list-reviews'),
    path('reviews/create/', create_review, name='create-review'),
    path('reviews/<int:pk>/update/', update_review, name='update-review'),
    path('reviews/<int:pk>/delete/', delete_review, name='delete-review'),
    
]

