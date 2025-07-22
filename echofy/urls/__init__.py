from django.urls import include, path

urlpatterns = [
    path('auth/', include('echofy.urls.auth')),
    path('sys/', include('echofy.urls.sys'))
]

