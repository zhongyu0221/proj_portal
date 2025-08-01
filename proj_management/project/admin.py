from django.contrib import admin
from .models import Project, Task, TaskAssignment, Issue, IssueStatusHistory, ProjectFile, ProjectActivity

# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_category', 'client_name', 'created_at', 'completed', 'completion_status']
    list_filter = ['project_category', 'completed', 'created_at']
    search_fields = ['title', 'description', 'client_name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'project', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'project']
    search_fields = ['original_filename', 'project__title']
    readonly_fields = ['uploaded_at']


@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'project', 'created_by', 'created_at']
    list_filter = ['activity_type', 'created_at', 'project']
    search_fields = ['description', 'project__title']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'priority', 'status', 'completed', 'due_date']
    list_filter = ['priority', 'status', 'completed', 'created_at']
    search_fields = ['title', 'description', 'project__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'assigned_at']
    list_filter = ['assigned_at']
    search_fields = ['task__title', 'user__user__username']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['task', 'category', 'found_by', 'found_at', 'solved']
    list_filter = ['category', 'solved', 'found_at']
    search_fields = ['description', 'task__title']


@admin.register(IssueStatusHistory)
class IssueStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['issue', 'status', 'changed_by', 'changed_at']
    list_filter = ['status', 'changed_at']
    search_fields = ['issue__description']
