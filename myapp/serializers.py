from django.contrib.auth import get_user_model,authenticate
from rest_framework import serializers
User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email","password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"].lower(), password=validated_data["password"]
        )
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data["email"].lower(),password=data["password"])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

from .models import FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender','receiver','status']
        read_only_fields = ['id','status']

class FriendRequestActionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=['accept','reject'])

    class Meta:
        model = FriendRequest
        fields = ['id','action']

    def update(self, instance,validated_data):
        action = validated_data.get('action')
        if action == 'accept':
            instance.status = 'accepted'
        elif action == 'reject':
            instance.status = 'rejected'
        instance.save()
        return instance
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name')

class PendingFriendRequestSerializer(serializers.ModelSerializer):
    sender_details = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ('id','sender', 'sender_details','created_at')

    def get_sender_details(self,obj):
        return {
            'username': obj.sender.username,
            'email': obj.sender.email,
            'first_name': obj.sender.first_name,
            'list_name': obj.sender.last_name,
        }
