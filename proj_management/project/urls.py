from .views import *
from django.urls import path

from project.views import *

app_name = 'projects'

urlpatterns = [
    # Project URLs
    path('project/create/', ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/complete/', ProjectCompleteView.as_view(), name='project_complete'),
    path('project/<int:pk>/upload-file/', ProjectFileUploadView.as_view(), name='project_upload_file'),
    path('project/<int:pk>/track-update/', ProjectUpdateView.as_view(), name='project_track_update'),
    path('project/project_list/', ProjectListView.as_view(), name='project_list'),
    path('project/project_card/', ProjectCardView.as_view(), name='project_card'),

    # File URLs
    path('project/file/<int:pk>/delete/', ProjectFileDeleteView.as_view(), name='project_file_delete'),

    # Task URLs
    path('task/list/', TaskListView.as_view(), name='task_list'),
    path('task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('task/<int:pk>/complete/', TaskCompleteView.as_view(), name='task_complete'),
    path('<int:project_id>/task/create/', TaskCreateView.as_view(), name='task_create'),
    path('<int:project_id>/task/create-ajax/', TaskCreateAjaxView.as_view(), name='task_create_ajax'),
    path('task/create/', TaskCreateView.as_view(), name='task_create_general'),
]