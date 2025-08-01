from django.db import models
from userprofiles.models import UserProfile
from django.utils import timezone
import os
# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=100, unique=True)
    PROJECT_CATEGORY_CHOICES = [
        ('EXPLORING', 'Exploring'),
        ('RESEARCH', 'Research'),
        ('DEVELOPMENT', 'Development'),
        ('TESTING', 'Testing'),
        ('DEPLOYMENT', 'Deployment'),
        ('MAINTENANCE', 'Maintenance'),
        ('OTHER', 'Other'),
    ]
    project_category = models.CharField(max_length=50,  choices=PROJECT_CATEGORY_CHOICES,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_name = models.CharField(max_length=100, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    files = models.FileField(upload_to='project_files/', blank=True, null=True)  # Keep for backward compatibility
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    @property
    def is_completed(self):
        return self.completed
    
    @property
    def has_pending_tasks(self):
        """Check if project has any incomplete tasks"""
        return self.tasks.filter(completed=False).exists()
    
    @property
    def pending_tasks_count(self):
        """Get count of incomplete tasks"""
        return self.tasks.filter(completed=False).count()
    
    @property
    def completion_status(self):
        """Get project completion status"""
        if self.completed:
            return 'COMPLETED'
        elif self.deadline and timezone.now() > self.deadline:
            return 'OVERDUE'
        else:
            return 'ACTIVE'
    
    @property
    def file_name(self):
        """Get the file name for display"""
        if self.files:
            return self.files.name.split('/')[-1]
        return None

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['created_at']


class ProjectFile(models.Model):
    """Model to store multiple files for a project"""
    project = models.ForeignKey(Project, related_name='project_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_files/')
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.original_filename} - {self.project.title}"
    
    @property
    def file_name(self):
        """Get the file name for display"""
        return self.original_filename
    
    @property
    def file_url(self):
        """Get the file URL"""
        return self.file.url if self.file else None
    
    def delete(self, *args, **kwargs):
        # Delete the actual file from storage
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Project File'
        verbose_name_plural = 'Project Files'
        ordering = ['-uploaded_at']


class ProjectActivity(models.Model):
    """Model to track project activities including file uploads"""
    ACTIVITY_TYPES = [
        ('PROJECT_CREATED', 'Project Created'),
        ('FILE_UPLOAD', 'File Upload'),
        ('FILE_DELETED', 'File Deleted'),
        ('TASK_CREATED', 'Task Created'),
        ('TASK_COMPLETED', 'Task Completed'),
        ('TASK_REOPENED', 'Task Reopened'),
        ('PROJECT_COMPLETED', 'Project Completed'),
        ('PROJECT_REOPENED', 'Project Reopened'),
        ('PROJECT_UPDATED', 'Project Updated'),
    ]
    
    project = models.ForeignKey(Project, related_name='activities', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Optional fields for specific activity types
    related_file = models.ForeignKey(ProjectFile, on_delete=models.SET_NULL, null=True, blank=True)
    related_task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.project.title}"
    
    class Meta:
        verbose_name = 'Project Activity'
        verbose_name_plural = 'Project Activities'
        ordering = ['-created_at']


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('REVIEW', 'Review'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='TODO')
    files = models.FileField(upload_to='task_files/', blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"
    
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return timezone.now() > self.due_date
        return False
    
    @property
    def progress_percentage(self):
        if self.status == 'COMPLETED':
            return 100
        elif self.status == 'REVIEW':
            return 75
        elif self.status == 'IN_PROGRESS':
            return 50
        elif self.status == 'TODO':
            return 0
        return 0

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-priority', 'due_date']


class TaskAssignment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('task', 'user')


class Issue(models.Model):
    task = models.ForeignKey('Task', related_name='issues', on_delete=models.CASCADE)
    CATEGORY_CHOICES = [
        ('product_design', 'Product design'),
        ('development', 'Development'),
        ('qa_testing', 'QA & Testing'),
        ('customer_queries', 'Customer queries'),
        ('r_and_d', 'R & D'),
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='product_design')
    found_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    description = models.TextField()
    found_at = models.DateTimeField(default=timezone.now)
    solved = models.BooleanField(default=False)

    def most_recent_status(self):
        latest_status = self.status_history.order_by('-changed_at').first()
        return latest_status.status if latest_status else None

    def __str__(self):
        return f"Issue for {self.task.title} by {self.found_by}"

    class Meta:
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'
        ordering = ['-found_at']


class IssueStatusHistory(models.Model):
    STATUS_CHOICES = [
        ('found', 'Found'),
        ('inprogress', 'In Progress'),
        ('complete', 'Complete'),
    ]
    issue = models.ForeignKey(Issue, related_name='status_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-changed_at']