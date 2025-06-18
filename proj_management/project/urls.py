from .views import *
from django.urls import path

from project.views import *

app_name = 'projects'

urlpatterns = [
   path('project/create/', ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
    path('project/project_list/', ProjectListView.as_view(), name='project_list'),
    path('project/project_card/', ProjectCardView.as_view(), name='project_card'),

    path('task/create/', TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),

    ]