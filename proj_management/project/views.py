from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from common.views import AjaxCreateView, AjaxUpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from .models import Project, Task, TaskAssignment, Issue, IssueStatusHistory, ProjectFile, ProjectActivity
from userprofiles.models import UserProfile
from .forms import *
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView


# PROJECT
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = reverse_lazy('projects:project_create')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Ensure current user has a UserProfile
        if not hasattr(self.request.user, 'userprofile'):
            UserProfile.objects.create(user=self.request.user)
        
        # Create activity record for project creation
        ProjectActivity.objects.create(
            project=self.object,
            activity_type='PROJECT_CREATED',
            description=f'Project "{self.object.title}" was created',
            created_by=self.request.user.userprofile
        )
        
        messages.success(self.request, f'Project "{self.object}" created successfully.')
        return response

class ProjectUpdateView(AjaxUpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    
    def get_success_url(self):
        # Check if changes were made and add them to URL parameters
        changes_made = []
        for field in ['title', 'description', 'project_category', 'client_name', 'deadline', 'budget', 'files']:
            if field in self.form.changed_data:
                changes_made.append(field)
        
        if changes_made:
            return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.id}) + f'?updated=true&changes={",".join(changes_made)}'
        else:
            return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.id}) + '?updated=true'
    
    def form_valid(self, form):
        # Store old values for comparison
        old_title = self.object.title if self.object.pk else None
        old_description = self.object.description if self.object.pk else None
        
        response = super().form_valid(form)
        
        # Check if significant changes were made
        changes_made = []
        if old_title and old_title != self.object.title:
            changes_made.append('title')
        if old_description and old_description != self.object.description:
            changes_made.append('description')
        
        # Add other field changes
        for field in ['project_category', 'client_name', 'deadline', 'budget', 'files']:
            if field in form.changed_data:
                changes_made.append(field)
        
        # Create activity record if changes were made
        if changes_made:
            # Ensure current user has a UserProfile
            if not hasattr(self.request.user, 'userprofile'):
                UserProfile.objects.create(user=self.request.user)
            
            ProjectActivity.objects.create(
                project=self.object,
                activity_type='PROJECT_UPDATED',
                description=f'Project "{self.object.title}" was updated (changes: {", ".join(changes_made)})',
                created_by=self.request.user.userprofile
            )
            messages.success(self.request, f'Project "{self.object.title}" updated successfully. Changes made: {", ".join(changes_made)}.')
        else:
            messages.info(self.request, f'Project "{self.object.title}" saved (no changes detected).')
        
        return response

class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        queryset = Project.objects.annotate(
            task_count=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__completed=True)),
            total_tasks=Count('tasks')
        ).order_by('-created_at')
        
        # Handle view all parameter
        view_all = self.request.GET.get('view_all')
        if view_all == 'true':
            self.paginate_by = None  # Disable pagination for view all
        
        # Handle filtering
        status_filter = self.request.GET.get('status')
        if status_filter:
            if status_filter == 'ongoing':
                queryset = queryset.filter(deadline__gte=timezone.now())
            elif status_filter == 'completed':
                queryset = queryset.filter(deadline__lt=timezone.now())
            elif status_filter == 'overdue':
                queryset = queryset.filter(deadline__lt=timezone.now())
        
        # Handle search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(client_name__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create a separate queryset for statistics (without pagination)
        stats_queryset = Project.objects.annotate(
            task_count=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__completed=True)),
            total_tasks=Count('tasks')
        ).order_by('-created_at')
        
        # Apply the same filters to stats queryset
        status_filter = self.request.GET.get('status')
        if status_filter:
            if status_filter == 'ongoing':
                stats_queryset = stats_queryset.filter(deadline__gte=timezone.now())
            elif status_filter == 'completed':
                stats_queryset = stats_queryset.filter(deadline__lt=timezone.now())
            elif status_filter == 'overdue':
                stats_queryset = stats_queryset.filter(deadline__lt=timezone.now())
        
        search = self.request.GET.get('search')
        if search:
            stats_queryset = stats_queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(client_name__icontains=search)
            )
        
        # Calculate project statistics using the stats queryset
        total_projects = stats_queryset.count()
        
        # Count projects by status (using the full queryset, not the paginated one)
        all_projects = Project.objects.all()
        ongoing_projects = all_projects.filter(completed=False, deadline__gte=timezone.now()).count()
        completed_projects = all_projects.filter(completed=True).count()
        overdue_projects = all_projects.filter(completed=False, deadline__lt=timezone.now()).count()
        
        # Get current filters
        current_status = self.request.GET.get('status', 'all')
        current_search = self.request.GET.get('search', '')
        view_all = self.request.GET.get('view_all') == 'true'
        
        context.update({
            'total_projects': total_projects,
            'ongoing_projects': ongoing_projects,
            'completed_projects': completed_projects,
            'overdue_projects': overdue_projects,
            'current_status': current_status,
            'current_search': current_search,
            'view_all': view_all,
        })
        
        return context



class ProjectCardView(ListView):
    model = Project
    template_name = 'project_card_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(task_count=Count('tasks')).order_by('-created_at')


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project-details.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get project tasks with assignments
        tasks = project.tasks.all().prefetch_related('taskassignment_set__user__user')
        
        # Calculate task statistics
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(completed=True).count()
        pending_tasks = tasks.filter(completed=False).count()
        
        # Get recent activities (including file uploads)
        recent_activities = project.activities.all()[:10]
        
        # Get project files
        project_files = project.project_files.all()
        
        # Get user profiles for task assignment - handle case where no UserProfiles exist
        try:
            userprofiles = UserProfile.objects.all()
            if not userprofiles.exists():
                # If no UserProfiles exist, create them for existing users
                from django.contrib.auth.models import User
                users = User.objects.all()
                for user in users:
                    if not hasattr(user, 'userprofile'):
                        UserProfile.objects.create(user=user)
                userprofiles = UserProfile.objects.all()
        except Exception as e:
            # Fallback to empty queryset if there's an error
            userprofiles = UserProfile.objects.none()
        
        context.update({
            'tasks': tasks,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'recent_activities': recent_activities,
            'project_files': project_files,
            'userprofiles': userprofiles,
        })
        
        return context



# TASK

class TaskCreateView(AjaxCreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'

    def dispatch(self, request, *args, **kwargs):
        # 确保只能通过项目详情页创建任务
        if 'project_id' not in kwargs:
            raise Http404("Task must be created from a project detail page")
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['project'] = self.project
        return initial

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.project.id})

    def form_valid(self, form):
        # Ensure current user has a UserProfile
        if not hasattr(self.request.user, 'userprofile'):
            UserProfile.objects.create(user=self.request.user)
        
        form.instance.created_by = self.request.user.userprofile
        form.instance.project = self.project
        response = super().form_valid(form)
        
        # Create task assignments for assigned users
        users = form.cleaned_data.get('assigned_users')
        for user in users:
            TaskAssignment.objects.create(task=self.object, user=user, assigned_at=timezone.now())
        
        # Create activity record for task creation
        ProjectActivity.objects.create(
            project=self.project,
            activity_type='TASK_CREATED',
            description=f'Task "{self.object.title}" was created',
            created_by=self.request.user.userprofile,
            related_task=self.object
        )
        
        # Add success message
        messages.success(self.request, f'Task "{self.object.title}" created successfully for project "{self.project.title}".')
        
        return response


class TaskUpdateView(AjaxUpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.id})

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f'Task "{self.object.title}" updated successfully.')
        return super().form_valid(form)


class TaskListView(ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = Task.objects.select_related('project', 'created_by').prefetch_related('taskassignment_set__user')
        # 过滤条件
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['status_choices'] = Task.STATUS_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        return context


class TaskDetailView(DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = self.object.taskassignment_set.select_related('user').all()
        context['issues'] = self.object.issues.select_related('found_by').all()
        return context


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('projects:task_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Task "{self.get_object()}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class TaskCompleteView(UpdateView):
    model = Task
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        
        # Ensure current user has a UserProfile
        if not hasattr(request.user, 'userprofile'):
            UserProfile.objects.create(user=request.user)
        
        # Toggle completion status
        task.completed = not task.completed
        if task.completed:
            task.status = 'COMPLETED'
        else:
            task.status = 'TODO'
        task.save()
        
        # Create activity record
        activity_type = 'TASK_COMPLETED' if task.completed else 'TASK_REOPENED'
        activity_description = f'Task "{task.title}" was {"completed" if task.completed else "reopened"}'
        
        ProjectActivity.objects.create(
            project=task.project,
            activity_type=activity_type,
            description=activity_description,
            created_by=request.user.userprofile,
            related_task=task
        )
        
        # Get project stats
        total_tasks = task.project.tasks.count()
        completed_tasks = task.project.tasks.filter(completed=True).count()
        pending_tasks = task.project.tasks.filter(completed=False).count()
        
        return JsonResponse({
            'success': True,
            'task_completed': task.completed,
            'task_id': task.id,
            'task_title': task.title,
            'activity_timestamp': timezone.now().strftime('%b %d, %Y'),
            'project_stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'has_pending_tasks': task.project.has_pending_tasks
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class ProjectCompleteView(UpdateView):
    model = Project
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        
        # Ensure current user has a UserProfile
        if not hasattr(request.user, 'userprofile'):
            UserProfile.objects.create(user=request.user)
        
        # Toggle completion status
        project.completed = not project.completed
        if project.completed:
            project.completed_at = timezone.now()
        else:
            project.completed_at = None
        project.save()
        
        # Create activity record
        activity_type = 'PROJECT_COMPLETED' if project.completed else 'PROJECT_REOPENED'
        activity_description = f'Project "{project.title}" was {"completed" if project.completed else "reopened"}'
        
        ProjectActivity.objects.create(
            project=project,
            activity_type=activity_type,
            description=activity_description,
            created_by=request.user.userprofile
        )
        
        # Get project stats
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(completed=True).count()
        pending_tasks = project.tasks.filter(completed=False).count()
        
        return JsonResponse({
            'success': True,
            'project_completed': project.completed,
            'project_status': project.completion_status,
            'project_title': project.title,
            'activity_timestamp': timezone.now().strftime('%b %d, %Y'),
            'project_stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'has_pending_tasks': project.has_pending_tasks
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class ProjectFileUploadView(UpdateView):
    model = Project
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            
            if 'files' in request.FILES:
                uploaded_files = []
                
                # Handle multiple files
                files = request.FILES.getlist('files')
                
                if not files:
                    return JsonResponse({
                        'success': False,
                        'message': 'No files were selected.'
                    }, status=400)
                
                with transaction.atomic():
                    for uploaded_file in files:
                        try:
                            # Ensure current user has a UserProfile
                            if not hasattr(request.user, 'userprofile'):
                                UserProfile.objects.create(user=request.user)
                            
                            # Create ProjectFile instance
                            project_file = ProjectFile.objects.create(
                                project=project,
                                file=uploaded_file,
                                original_filename=uploaded_file.name,
                                uploaded_by=request.user.userprofile
                            )
                            
                            # Create activity record
                            ProjectActivity.objects.create(
                                project=project,
                                activity_type='FILE_UPLOAD',
                                description=f'File "{uploaded_file.name}" was uploaded',
                                created_by=request.user.userprofile,
                                related_file=project_file
                            )
                            
                            uploaded_files.append({
                                'file_name': uploaded_file.name,
                                'file_url': project_file.file.url,
                                'uploaded_at': project_file.uploaded_at.strftime('%b %d, %Y')
                            })
                        except Exception as e:
                            return JsonResponse({
                                'success': False,
                                'message': f'Error uploading file {uploaded_file.name}: {str(e)}'
                            }, status=500)
                
                return JsonResponse({
                    'success': True,
                    'files': uploaded_files,
                    'message': f'{len(uploaded_files)} file(s) uploaded successfully.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No files were uploaded.'
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectFileDeleteView(DeleteView):
    model = ProjectFile
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        try:
            project_file = self.get_object()
            project = project_file.project
            file_name = project_file.original_filename
            
            # Ensure current user has a UserProfile
            if not hasattr(request.user, 'userprofile'):
                UserProfile.objects.create(user=request.user)
            
            # Create activity record before deleting
            ProjectActivity.objects.create(
                project=project,
                activity_type='FILE_DELETED',
                description=f'File "{file_name}" was deleted',
                created_by=request.user.userprofile
            )
            
            # Delete the file
            project_file.delete()
            
            return JsonResponse({
                'success': True,
                'file_name': file_name,
                'message': f'File "{file_name}" deleted successfully.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting file: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TaskCreateAjaxView(CreateView):
    model = Task
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        
        try:
            # Ensure current user has a UserProfile
            if not hasattr(request.user, 'userprofile'):
                UserProfile.objects.create(user=request.user)
            
            # Create task
            task = Task.objects.create(
                project=project,
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                priority=request.POST.get('priority', 'MEDIUM'),
                status=request.POST.get('status', 'TODO'),
                due_date=request.POST.get('due_date') if request.POST.get('due_date') else None,
                created_by=request.user.userprofile
            )
            
            # Handle assigned users
            assigned_users = request.POST.getlist('assigned_users')
            for user_id in assigned_users:
                user = get_object_or_404(UserProfile, pk=user_id)
                TaskAssignment.objects.create(task=task, user=user, assigned_at=timezone.now())
            
            # Create activity record
            ProjectActivity.objects.create(
                project=project,
                activity_type='TASK_CREATED',
                description=f'Task "{task.title}" was created',
                created_by=request.user.userprofile,
                related_task=task
            )
            
            return JsonResponse({
                'success': True,
                'task_id': task.id,
                'task_title': task.title,
                'task_status': task.get_status_display(),
                'task_priority': task.get_priority_display(),
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                'assigned_users': [assignment.user.user.username for assignment in task.taskassignment_set.all()],
                'message': f'Task "{task.title}" created successfully.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating task: {str(e)}'
            }, status=400)