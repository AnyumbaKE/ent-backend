from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TestModel, TestSession, Blog, PasswordResetOTP, ReviewModel
import re


User = get_user_model()


class TestModelSerializer(serializers.ModelSerializer):
    added_by = serializers.StringRelatedField()

    class Meta:
        model = TestModel
        fields = ['id', 'type', 'question', 'audio', 'correctAnswer', 'level', 'added_by','language']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'staff'),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'full_name', 'activated']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate_email(self, value):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value


class TestSessionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = TestSession
        fields = [
            'id',
            'user',
            'mode',
            'started_at',
            'correct_no',
            'closed',
        ]
        read_only_fields = ['id', 'user', 'started_at', 'correct_no', 'closed']



class BlogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'user', 'title', 'text', 'image_url', 'created_at', 'approval_status']
        read_only_fields = ['user', 'created_at']



class PasswordResetOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PasswordResetOTP
        fields = ['id', 'email', 'otp', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receiver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    receiver_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReviewModel
        fields = ['id', 'sender', 'receiver', 'receiver_username', 'title', 'text']

    def get_sender(self, obj):
        return obj.sender.username

    def get_receiver_username(self, obj):
        return obj.receiver.username

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)