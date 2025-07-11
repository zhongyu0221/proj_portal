from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from common.views import AjaxCreateView, AjaxUpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import *
from .forms import *
from django.db.models import Count, Q

from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView


# PROJECT
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = reverse_lazy('projects:project_create')


    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Project "{self.object}" created successfully.')
        return response

class ProjectUpdateView(AjaxUpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/project_create.html'
    success_url = '/projects/'

class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(
            task_count=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__completed=True)),
            total_tasks=Count('tasks')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate project statistics
        projects = context['projects']
        total_projects = projects.count()
        
        # Count projects by status (you can customize these based on your project status field)
        ongoing_projects = projects.filter(deadline__gte=timezone.now()).count()
        completed_projects = projects.filter(deadline__lt=timezone.now()).count()
        cancelled_projects = 0  # Add logic based on your project status
        postponed_projects = 0  # Add logic based on your project status
        
        context.update({
            'total_projects': total_projects,
            'ongoing_projects': ongoing_projects,
            'completed_projects': completed_projects,
            'cancelled_projects': cancelled_projects,
            'postponed_projects': postponed_projects,
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
        project = self.object
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(completed=True).count()
        open_tasks = project.tasks.filter(completed=False).count()
        
        # Calculate completion percentage
        completion_percentage = 0
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100
        
        context['total_tasks'] = total_tasks
        context['completed_tasks'] = completed_tasks
        context['open_tasks'] = open_tasks
        context['completion_percentage'] = completion_percentage
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
        form.instance.created_by = self.request.user.userprofile
        form.instance.project = self.project
        response = super().form_valid(form)
        
        # Create task assignments for assigned users
        users = form.cleaned_data.get('assigned_users')
        for user in users:
            TaskAssignment.objects.create(task=self.object, user=user, assigned_at=timezone.now())
        
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