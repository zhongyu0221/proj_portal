import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from project.models import Project, Task
from userprofiles.models import UserProfile
from datetime import timedelta

CATEGORIES = [
    'EXPLORING', 'RESEARCH', 'DEVELOPMENT', 'TESTING', 'DEPLOYMENT', 'MAINTENANCE', 'OTHER'
]

class Command(BaseCommand):
    help = 'Generate test projects and tasks for quarterly trend chart testing.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of projects to create')

    def handle(self, *args, **options):
        count = options['count']
        users = list(UserProfile.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No UserProfiles found. Please create at least one user.'))
            return
        
        today = timezone.now().date()
        
        # Generate projects spanning the past year (365 days)
        for i in range(count):
            # Random date within the past year
            days_ago = random.randint(0, 365)
            deadline = today - timedelta(days=days_ago)
            
            # Ensure some projects are completed, some active, some overdue
            if i < count * 0.3:  # 30% completed projects
                deadline = today - timedelta(days=random.randint(30, 365))
                status_distribution = ['COMPLETED'] * 8 + ['TODO', 'IN_PROGRESS', 'REVIEW'] * 2
            elif i < count * 0.6:  # 30% active projects
                deadline = today + timedelta(days=random.randint(1, 90))
                status_distribution = ['TODO', 'IN_PROGRESS', 'REVIEW'] * 8 + ['COMPLETED'] * 2
            else:  # 40% overdue projects
                deadline = today - timedelta(days=random.randint(1, 30))
                status_distribution = ['TODO', 'IN_PROGRESS', 'REVIEW'] * 8 + ['COMPLETED'] * 2
            
            category = random.choice(CATEGORIES)
            project = Project.objects.create(
                title=f'Test Project {timezone.now().strftime("%Y%m%d%H%M%S")}_{i}',
                project_category=category,
                description='Auto-generated for quarterly trend chart testing.',
                created_at=deadline - timedelta(days=random.randint(1, 30)),
                deadline=deadline,
                client_name=f'Client {random.randint(1, 10)}',
                budget=random.randint(1000, 10000)
            )
            
            # Create 2-5 tasks per project
            num_tasks = random.randint(2, 5)
            completed_tasks = 0
            
            for t in range(num_tasks):
                status = random.choice(status_distribution)
                completed = status == 'COMPLETED'
                if completed:
                    completed_tasks += 1
                    
                task = Task.objects.create(
                    project=project,
                    title=f'Task {t+1} for {project.title}',
                    description='Auto-generated task for trend testing',
                    priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                    status=status,
                    due_date=project.deadline,
                    completed=completed,
                    created_by=random.choice(users)
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created project: {project.title} (Deadline: {deadline}, Tasks: {num_tasks}, Completed: {completed_tasks})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Generated {count} projects with tasks spanning the past year for quarterly trend testing.'
            )
        ) 