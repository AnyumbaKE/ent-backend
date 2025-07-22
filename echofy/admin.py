from django.contrib import admin
from .models import CustomUser
from .models import PasswordResetOTP
from echofy.models import TestModel, TestSession, Blog,ReviewModel
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(PasswordResetOTP)
admin.site.register(TestModel)
admin.site.register(TestSession)
admin.site.register(Blog)
admin.site.register(ReviewModel)


