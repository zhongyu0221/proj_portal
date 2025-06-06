from .views import *
from django.urls import path

app_name = 'userprofiles'
urlpatterns = [
    path('userprofile_list/', UserProfileListView.as_view(), name='userprofile_list'),

    ]

