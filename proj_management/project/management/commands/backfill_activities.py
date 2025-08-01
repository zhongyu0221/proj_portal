from django.core.management.base import BaseCommand
from django.utils import timezone
from project.models import Project, Task, ProjectActivity
from userprofiles.models import UserProfile


class Command(BaseCommand):
    help = 'Backfill activity records for existing tasks and projects'

    def handle(self, *args, **options):
        self.stdout.write('Starting activity backfill...')
        
        # Get all projects
        projects = Project.objects.all()
        
        for project in projects:
            self.stdout.write(f'Processing project: {project.title}')
            
            # Create project creation activity if it doesn't exist
            if not ProjectActivity.objects.filter(project=project, activity_type='PROJECT_CREATED').exists():
                ProjectActivity.objects.create(
                    project=project,
                    activity_type='PROJECT_CREATED',
                    description=f'Project "{project.title}" was created',
                    created_by=UserProfile.objects.first(),  # Use first user as fallback
                    created_at=project.created_at
                )
                self.stdout.write(f'  - Created project creation activity')
            
            # Create task creation activities for existing tasks
            tasks = project.tasks.all()
            for task in tasks:
                if not ProjectActivity.objects.filter(project=project, activity_type='TASK_CREATED', related_task=task).exists():
                    ProjectActivity.objects.create(
                        project=project,
                        activity_type='TASK_CREATED',
                        description=f'Task "{task.title}" was created',
                        created_by=task.created_by if task.created_by else UserProfile.objects.first(),
                        related_task=task,
                        created_at=task.created_at
                    )
                    self.stdout.write(f'  - Created task creation activity for: {task.title}')
                
                # Create task completion activities for completed tasks
                if task.completed and not ProjectActivity.objects.filter(project=project, activity_type='TASK_COMPLETED', related_task=task).exists():
                    ProjectActivity.objects.create(
                        project=project,
                        activity_type='TASK_COMPLETED',
                        description=f'Task "{task.title}" was completed',
                        created_by=task.created_by if task.created_by else UserProfile.objects.first(),
                        related_task=task,
                        created_at=task.updated_at
                    )
                    self.stdout.write(f'  - Created task completion activity for: {task.title}')
            
            # Create project completion activity if project is completed
            if project.completed and not ProjectActivity.objects.filter(project=project, activity_type='PROJECT_COMPLETED').exists():
                ProjectActivity.objects.create(
                    project=project,
                    activity_type='PROJECT_COMPLETED',
                    description=f'Project "{project.title}" was completed',
                    created_by=UserProfile.objects.first(),
                    created_at=project.completed_at or project.updated_at
                )
                self.stdout.write(f'  - Created project completion activity')
        
        self.stdout.write(self.style.SUCCESS('Activity backfill completed successfully!')) 