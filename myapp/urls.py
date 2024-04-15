from django.urls import path
from.views import SignupView,LoginView,SendFriendRequestView,FriendRequestActionview,ListFriendView,PendingFriendRequestView
from django.urls import path

urlpatterns =[
    path('signup/', SignupView.as_view(),name='signup'),
    path('login/',LoginView.as_view(),name='login'),
    path('send-friend-request/',SendFriendRequestView.as_view(),name='send-friend-request'),
    path('friend_request_actions/<int:pk>/',FriendRequestActionview.as_view(), name+'friend-request-action'),
    path('list-friends/', ListfriendsView.as_view(),name='list-friend')
    path('pending-friend-request/',PendingFriendRequestsView.as_view(), name+'Pending-friend-requests'),
]