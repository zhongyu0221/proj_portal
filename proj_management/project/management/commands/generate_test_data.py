from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from userprofiles.models import UserProfile
from project.models import Project, Task, TaskAssignment, Issue, IssueStatusHistory
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = '生成测试数据用于开发和测试'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='要创建的用户数量 (默认: 10)'
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=20,
            help='要创建的项目数量 (默认: 20)'
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=50,
            help='要创建的任务数量 (默认: 50)'
        )
        parser.add_argument(
            '--issues',
            type=int,
            default=15,
            help='要创建的问题数量 (默认: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='在生成新数据前清除现有数据'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('清除现有数据...')
            IssueStatusHistory.objects.all().delete()
            Issue.objects.all().delete()
            TaskAssignment.objects.all().delete()
            Task.objects.all().delete()
            Project.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('数据已清除'))

        # 生成用户数据
        self.stdout.write('生成用户数据...')
        users = self.create_users(options['users'])
        self.stdout.write(self.style.SUCCESS(f'已创建 {len(users)} 个用户'))

        # 生成项目数据
        self.stdout.write('生成项目数据...')
        projects = self.create_projects(options['projects'])
        self.stdout.write(self.style.SUCCESS(f'已创建 {len(projects)} 个项目'))

        # 生成任务数据
        self.stdout.write('生成任务数据...')
        tasks = self.create_tasks(options['tasks'], projects, users)
        self.stdout.write(self.style.SUCCESS(f'已创建 {len(tasks)} 个任务'))

        # 生成任务分配数据
        self.stdout.write('生成任务分配数据...')
        assignments = self.create_task_assignments(tasks, users)
        self.stdout.write(self.style.SUCCESS(f'已创建 {len(assignments)} 个任务分配'))

        # 生成问题数据
        self.stdout.write('生成问题数据...')
        issues = self.create_issues(options['issues'], tasks, users)
        self.stdout.write(self.style.SUCCESS(f'已创建 {len(issues)} 个问题'))

        self.stdout.write(self.style.SUCCESS('测试数据生成完成!'))

    def create_users(self, count):
        """创建用户和用户档案"""
        users = []
        user_levels = [UserProfile.TECHNOLOGIST, UserProfile.MANAGER, UserProfile.DIRECTOR, UserProfile.SUPERADMIN]
        
        for i in range(count):
            # 创建用户
            user = User.objects.create_user(
                username=f'user{i+1}',
                first_name=f'User{i+1}',
                last_name=f'Test{i+1}',
                email=f'user{i+1}@example.com',
                password='testpass123'
            )
            
            # 创建用户档案
            userprofile = UserProfile.objects.create(
                user=user,
                phone=f'+1{random.randint(1000000000, 9999999999)}',
                city=random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']),
                user_level=random.choice(user_levels)
            )
            
            users.append(userprofile)
        
        return users

    def create_projects(self, count):
        """创建项目"""
        projects = []
        categories = [choice[0] for choice in Project.PROJECT_CATEGORY_CHOICES]
        clients = ['TechCorp', 'InnovateLabs', 'DigitalSolutions', 'FutureTech', 'SmartSystems', 'DataFlow', 'CloudWorks', 'NextGen', 'EliteTech', 'PrimeSolutions']
        
        for i in range(count):
            project = Project.objects.create(
                title=f'Project {i+1}: {random.choice(["Web Application", "Mobile App", "API Development", "Database Design", "Cloud Migration", "Security Audit", "Performance Optimization", "UI/UX Redesign", "Testing Framework", "Deployment Pipeline"])}',
                description=f'This is a comprehensive project description for project {i+1}. It includes various aspects of development and implementation.',
                project_category=random.choice(categories),
                created_at=timezone.now() - timedelta(days=random.randint(1, 365)),
                deadline=timezone.now() + timedelta(days=random.randint(30, 180)),
                client_name=random.choice(clients),
                budget=Decimal(random.randint(5000, 100000))
            )
            projects.append(project)
        
        return projects

    def create_tasks(self, count, projects, users):
        """创建任务"""
        tasks = []
        priorities = [choice[0] for choice in Task.PRIORITY_CHOICES]
        statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        
        for i in range(count):
            project = random.choice(projects)
            created_by = random.choice(users)
            
            task = Task.objects.create(
                project=project,
                title=f'Task {i+1}: {random.choice(["Design Review", "Code Implementation", "Testing", "Documentation", "Bug Fix", "Feature Development", "Performance Testing", "Security Review", "User Testing", "Deployment"])}',
                description=f'Detailed description for task {i+1}. This task involves various development activities.',
                priority=random.choice(priorities),
                status=random.choice(statuses),
                due_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                completed=random.choice([True, False]),
                created_by=created_by
            )
            tasks.append(task)
        
        return tasks

    def create_task_assignments(self, tasks, users):
        """创建任务分配"""
        assignments = []
        
        for task in tasks:
            # 为每个任务分配1-3个用户
            num_assignments = random.randint(1, min(3, len(users)))
            assigned_users = random.sample(users, num_assignments)
            
            for user in assigned_users:
                assignment, created = TaskAssignment.objects.get_or_create(
                    task=task,
                    user=user,
                    defaults={'assigned_at': timezone.now() - timedelta(days=random.randint(1, 30))}
                )
                if created:
                    assignments.append(assignment)
        
        return assignments

    def create_issues(self, count, tasks, users):
        """创建问题"""
        issues = []
        categories = [choice[0] for choice in Issue.CATEGORY_CHOICES]
        
        for i in range(count):
            task = random.choice(tasks)
            found_by = random.choice(users)
            
            issue = Issue.objects.create(
                task=task,
                category=random.choice(categories),
                found_by=found_by,
                description=f'Issue {i+1}: {random.choice(["Performance degradation", "Security vulnerability", "UI inconsistency", "Database connection error", "API timeout", "Memory leak", "Cross-browser compatibility", "Mobile responsiveness", "Accessibility issue", "Integration problem"])}',
                found_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                solved=random.choice([True, False])
            )
            
            # 创建问题状态历史
            statuses = [choice[0] for choice in IssueStatusHistory.STATUS_CHOICES]
            num_statuses = random.randint(1, len(statuses))
            selected_statuses = random.sample(statuses, num_statuses)
            
            for j, status in enumerate(selected_statuses):
                IssueStatusHistory.objects.create(
                    issue=issue,
                    status=status,
                    changed_by=random.choice(users),
                    changed_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
            
            issues.append(issue)
        
        return issues 