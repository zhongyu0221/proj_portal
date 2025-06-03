from django.db import models
from userprofiles.models import UserProfile
from django.utils import timezone
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['created_at']


class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['due_date']


class TaskAssignment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('task', 'user')


class Issue(models.Model):
    task = models.ForeignKey('Task', related_name='issues', on_delete=models.CASCADE)
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