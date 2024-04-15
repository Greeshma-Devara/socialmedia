from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSignupSerializer, UserLoginSerializer
from rest_framework import generics, status, permissions
from .models import FriendRequest
from .serializers import FriendRequestSerializer, FriendRequestActionSerializer, PendingFriendRequestSerializer


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created= Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, pagination
from .serializers import UserSerializer

User = get_user_model()

class UserSearchPagination(pagination.PageNumberPagination)
    page_size = 10

class UserSearchView(generics.ListAPIViews):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    serializer_class = UserSearchPagination

    def get_queryset(self):
        search_keyword = self.request.query_params.get('search','').lower()
        if search_keyword:
            if User.objects.filter(email_iexact=search_keyword).exists():
                return User.objects.filter(email_iexact=search_keyword)
            return User.objects.filter(
                Q(first_name__icontains=search_keyword)
                Q(last_name__icontains=search_keyword)
            )
        return User.objects.none()
    

class SendFriendRequestView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class FriendRequestActionview(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestActionSerializer

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        if friend_request.receiver != request.User:
            return Response({"detail": "You don't have permission to change this friend request."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
    
class ListFriendView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return FriendRequest.get_friends(self.request.user)
    
class PendingFriendRequestView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PendingFriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='sent')
    

from django.core.cache import cache
from django.utils.timezone import now
from datetime import timedelta

def has_exceeded_rate_limit(user, max_requests=3, timeframe=timedelta(minutes=1)):
    cache_key = f'friend_request_limit_{user.id}'
    request_history = cache.get(cache_key, [])
    request_history = [request_time for request_time in request_history if now() - request_time < timeframe ]
    if len(request_history) >= max_requests:
        return True
    else:
        request_history.appendf(now())   
        cache.set(cache_key, request_history, timeout=int(timeframe.total_seconds()))
        return False
    
class SendFriendRequestView(generics.CreateAPIView):
    permission_classes= [permissions.IsAuthenticated]
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def perform_create(self, serializer):
        if has_exceeded_rate_limit(self.request.user):
            response = Response({
                'detail': 'You have sent too many friend requests. Please wait a minute before trying again.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            self.raise_exception = True
            self.headers = self.default_response_headers
            return response
        serializer.save(sender=self.request.user)
        


