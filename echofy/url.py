from dj_database_url import include, path

urlpatterns = [
    path('auth/', include('echofy.urls.auth')),
    path('sys/', include('echofy.blog.sys')),
]

