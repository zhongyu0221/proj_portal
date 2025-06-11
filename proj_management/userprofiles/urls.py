from .views import *
from django.urls import path

app_name = 'userprofiles'
urlpatterns = [
    path('userprofile_list/', UserProfileListView.as_view(), name='userprofile_list'),
    path('member/create/', UserProfileCreateView.as_view(), name='member_create'),
    path('member/<int:pk>/update/', UserProfileUpdateView.as_view(), name='member_edit'),
    ]

