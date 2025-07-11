from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from userprofiles.models import UserProfile
from .models import Project, Task, TaskAssignment, Issue, IssueStatusHistory
from .forms import ProjectForm, TaskForm
import factory
from factory.django import DjangoModelFactory
from factory import Faker
from decimal import Decimal
import os


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = Faker('user_name')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    email = Faker('email')
    password = Faker('password')


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    phone = Faker('phone_number')
    city = Faker('city')
    user_level = UserProfile.TECHNOLOGIST


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project
    
    title = Faker('sentence', nb_words=3)
    description = Faker('text', max_nb_chars=200)
    project_category = Project.PROJECT_CATEGORY_CHOICES[0][0]  # EXPLORING
    created_at = Faker('date_time_this_year')
    deadline = Faker('future_datetime', end_date='+30d')
    client_name = Faker('company')
    budget = Faker('pydecimal', left_digits=6, right_digits=2, positive=True)


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
    
    project = factory.SubFactory(ProjectFactory)
    title = Faker('sentence', nb_words=4)
    description = Faker('text', max_nb_chars=300)
    priority = Task.PRIORITY_CHOICES[1][0]  # MEDIUM
    status = Task.STATUS_CHOICES[0][0]  # TODO
    due_date = Faker('future_datetime', end_date='+14d')
    completed = False
    created_by = factory.SubFactory(UserProfileFactory)


class TaskAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = TaskAssignment
    
    task = factory.SubFactory(TaskFactory)
    user = factory.SubFactory(UserProfileFactory)


class IssueFactory(DjangoModelFactory):
    class Meta:
        model = Issue
    
    task = factory.SubFactory(TaskFactory)
    category = Issue.CATEGORY_CHOICES[0][0]  # product_design
    found_by = factory.SubFactory(UserProfileFactory)
    description = Faker('text', max_nb_chars=200)
    solved = False


class IssueStatusHistoryFactory(DjangoModelFactory):
    class Meta:
        model = IssueStatusHistory
    
    issue = factory.SubFactory(IssueFactory)
    status = IssueStatusHistory.STATUS_CHOICES[0][0]  # found
    changed_by = factory.SubFactory(UserProfileFactory)


class ProjectModelTest(TestCase):
    """Project模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.project = ProjectFactory()
    
    def test_project_creation(self):
        """测试Project创建"""
        self.assertIsNotNone(self.project.title)
        self.assertIsNotNone(self.project.description)
        self.assertIsNotNone(self.project.project_category)
        self.assertIsNotNone(self.project.created_at)
        self.assertIsNotNone(self.project.updated_at)
    
    def test_project_str_method(self):
        """测试__str__方法"""
        self.assertEqual(str(self.project), self.project.title)
    
    def test_project_meta_ordering(self):
        """测试Meta排序"""
        project2 = ProjectFactory(created_at=timezone.now() - timezone.timedelta(days=1))
        project3 = ProjectFactory(created_at=timezone.now() + timezone.timedelta(days=1))
        
        projects = Project.objects.all()
        self.assertEqual(projects[0], project2)  # 最早的
        self.assertEqual(projects[1], self.project)  # 中间的
        self.assertEqual(projects[2], project3)  # 最晚的
    
    def test_project_category_choices(self):
        """测试项目类别选择"""
        for choice in Project.PROJECT_CATEGORY_CHOICES:
            self.project.project_category = choice[0]
            self.project.save()
            self.assertEqual(self.project.project_category, choice[0])
    
    def test_project_budget_validation(self):
        """测试预算验证"""
        self.project.budget = Decimal('1000.50')
        self.project.save()
        self.assertEqual(self.project.budget, Decimal('1000.50'))
        
        # 测试负数预算
        self.project.budget = Decimal('-100.00')
        self.project.save()
        self.assertEqual(self.project.budget, Decimal('-100.00'))


class TaskModelTest(TestCase):
    """Task模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.userprofile = UserProfileFactory()
        self.project = ProjectFactory()
        self.task = TaskFactory(project=self.project, created_by=self.userprofile)
    
    def test_task_creation(self):
        """测试Task创建"""
        self.assertIsNotNone(self.task.title)
        self.assertIsNotNone(self.task.project)
        self.assertIsNotNone(self.task.priority)
        self.assertIsNotNone(self.task.status)
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)
    
    def test_task_str_method(self):
        """测试__str__方法"""
        expected_str = f"{self.task.title} - {self.task.project.title}"
        self.assertEqual(str(self.task), expected_str)
    
    def test_task_priority_choices(self):
        """测试优先级选择"""
        for choice in Task.PRIORITY_CHOICES:
            self.task.priority = choice[0]
            self.task.save()
            self.assertEqual(self.task.priority, choice[0])
    
    def test_task_status_choices(self):
        """测试状态选择"""
        for choice in Task.STATUS_CHOICES:
            self.task.status = choice[0]
            self.task.save()
            self.assertEqual(self.task.status, choice[0])
    
    def test_task_is_overdue_property(self):
        """测试is_overdue属性"""
        # 未完成且过期
        self.task.due_date = timezone.now() - timezone.timedelta(days=1)
        self.task.completed = False
        self.task.save()
        self.assertTrue(self.task.is_overdue)
        
        # 已完成且过期
        self.task.completed = True
        self.task.save()
        self.assertFalse(self.task.is_overdue)
        
        # 未完成且未过期
        self.task.due_date = timezone.now() + timezone.timedelta(days=1)
        self.task.completed = False
        self.task.save()
        self.assertFalse(self.task.is_overdue)
    
    def test_task_progress_percentage_property(self):
        """测试progress_percentage属性"""
        # TODO状态
        self.task.status = 'TODO'
        self.task.save()
        self.assertEqual(self.task.progress_percentage, 0)
        
        # IN_PROGRESS状态
        self.task.status = 'IN_PROGRESS'
        self.task.save()
        self.assertEqual(self.task.progress_percentage, 50)
        
        # REVIEW状态
        self.task.status = 'REVIEW'
        self.task.save()
        self.assertEqual(self.task.progress_percentage, 75)
        
        # COMPLETED状态
        self.task.status = 'COMPLETED'
        self.task.save()
        self.assertEqual(self.task.progress_percentage, 100)
    
    def test_task_meta_ordering(self):
        """测试Meta排序"""
        task2 = TaskFactory(project=self.project, priority='HIGH')
        task3 = TaskFactory(project=self.project, priority='LOW')
        
        tasks = Task.objects.all()
        # 按优先级降序，然后按到期日期
        self.assertEqual(tasks[0], task2)  # HIGH
        self.assertEqual(tasks[1], self.task)  # MEDIUM
        self.assertEqual(tasks[2], task3)  # LOW


class TaskAssignmentModelTest(TestCase):
    """TaskAssignment模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.task = TaskFactory()
        self.userprofile = UserProfileFactory()
        self.assignment = TaskAssignmentFactory(task=self.task, user=self.userprofile)
    
    def test_task_assignment_creation(self):
        """测试TaskAssignment创建"""
        self.assertEqual(self.assignment.task, self.task)
        self.assertEqual(self.assignment.user, self.userprofile)
        self.assertIsNotNone(self.assignment.assigned_at)
    
    def test_task_assignment_unique_constraint(self):
        """测试唯一性约束"""
        # 尝试为同一任务和用户创建重复分配应该失败
        with self.assertRaises(Exception):
            TaskAssignment.objects.create(task=self.task, user=self.userprofile)


class IssueModelTest(TestCase):
    """Issue模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.task = TaskFactory()
        self.userprofile = UserProfileFactory()
        self.issue = IssueFactory(task=self.task, found_by=self.userprofile)
    
    def test_issue_creation(self):
        """测试Issue创建"""
        self.assertEqual(self.issue.task, self.task)
        self.assertEqual(self.issue.found_by, self.userprofile)
        self.assertIsNotNone(self.issue.description)
        self.assertIsNotNone(self.issue.found_at)
        self.assertFalse(self.issue.solved)
    
    def test_issue_str_method(self):
        """测试__str__方法"""
        expected_str = f"Issue for {self.issue.task.title} by {self.issue.found_by}"
        self.assertEqual(str(self.issue), expected_str)
    
    def test_issue_category_choices(self):
        """测试类别选择"""
        for choice in Issue.CATEGORY_CHOICES:
            self.issue.category = choice[0]
            self.issue.save()
            self.assertEqual(self.issue.category, choice[0])
    
    def test_issue_most_recent_status(self):
        """测试most_recent_status方法"""
        # 没有状态历史
        self.assertIsNone(self.issue.most_recent_status())
        
        # 添加状态历史
        status_history = IssueStatusHistoryFactory(issue=self.issue, status='found')
        self.assertEqual(self.issue.most_recent_status(), 'found')
        
        # 添加更新的状态历史
        IssueStatusHistoryFactory(issue=self.issue, status='inprogress')
        self.assertEqual(self.issue.most_recent_status(), 'inprogress')


class ProjectViewTest(TestCase):
    """Project视图测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
        self.project = ProjectFactory()
        self.client.force_login(self.user)
    
    def test_project_list_view(self):
        """测试项目列表视图"""
        response = self.client.get(reverse('projects:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
    
    def test_project_card_view(self):
        """测试项目卡片视图"""
        response = self.client.get(reverse('projects:project_card'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
    
    def test_project_create_view(self):
        """测试项目创建视图"""
        response = self.client.get(reverse('projects:project_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_project_detail_view(self):
        """测试项目详情视图"""
        response = self.client.get(reverse('projects:project_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
    
    def test_project_update_view(self):
        """测试项目更新视图"""
        response = self.client.get(reverse('projects:project_update', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_project_delete_view(self):
        """测试项目删除视图"""
        response = self.client.get(reverse('projects:project_delete', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)


class TaskViewTest(TestCase):
    """Task视图测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
        self.project = ProjectFactory()
        self.task = TaskFactory(project=self.project, created_by=self.userprofile)
        self.client.force_login(self.user)
    
    def test_task_list_view(self):
        """测试任务列表视图"""
        response = self.client.get(reverse('projects:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
    
    def test_task_create_view(self):
        """测试任务创建视图"""
        response = self.client.get(reverse('projects:task_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_task_detail_view(self):
        """测试任务详情视图"""
        response = self.client.get(reverse('projects:task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
    
    def test_task_update_view(self):
        """测试任务更新视图"""
        response = self.client.get(reverse('projects:task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_task_delete_view(self):
        """测试任务删除视图"""
        response = self.client.get(reverse('projects:task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)


class ProjectFormTest(TestCase):
    """Project表单测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.project = ProjectFactory()
    
    def test_project_form_valid(self):
        """测试有效表单数据"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test Description',
            'project_category': 'DEVELOPMENT',
            'client_name': 'Test Client',
            'budget': '10000.00',
        }
        form = ProjectForm(data=form_data, instance=self.project)
        self.assertTrue(form.is_valid())
    
    def test_project_form_invalid(self):
        """测试无效表单数据"""
        form_data = {
            'title': '',  # 必填字段为空
            'description': 'Test Description',
            'project_category': 'INVALID_CATEGORY',
            'client_name': 'Test Client',
            'budget': 'invalid_budget',
        }
        form = ProjectForm(data=form_data, instance=self.project)
        self.assertFalse(form.is_valid())
    
    def test_project_form_unique_title(self):
        """测试标题唯一性"""
        existing_project = ProjectFactory(title='Existing Project')
        
        form_data = {
            'title': 'Existing Project',  # 重复标题
            'description': 'Test Description',
            'project_category': 'DEVELOPMENT',
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())


class TaskFormTest(TestCase):
    """Task表单测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.project = ProjectFactory()
        self.userprofile = UserProfileFactory()
        self.task = TaskFactory(project=self.project, created_by=self.userprofile)
    
    def test_task_form_valid(self):
        """测试有效表单数据"""
        form_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 'HIGH',
            'status': 'IN_PROGRESS',
            'project': self.project.pk,
        }
        form = TaskForm(data=form_data, instance=self.task)
        self.assertTrue(form.is_valid())
    
    def test_task_form_invalid(self):
        """测试无效表单数据"""
        form_data = {
            'title': '',  # 必填字段为空
            'description': 'Test Description',
            'priority': 'INVALID_PRIORITY',
            'status': 'INVALID_STATUS',
            'project': self.project.pk,
        }
        form = TaskForm(data=form_data, instance=self.task)
        self.assertFalse(form.is_valid())


class ProjectIntegrationTest(TestCase):
    """Project集成测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
        self.client.force_login(self.user)
    
    def test_project_create_workflow(self):
        """测试项目创建工作流"""
        project_data = {
            'title': 'New Test Project',
            'description': 'A new test project',
            'project_category': 'DEVELOPMENT',
            'client_name': 'Test Client',
            'budget': '5000.00',
        }
        
        response = self.client.post(reverse('projects:project_create'), project_data)
        self.assertEqual(response.status_code, 302)  # 重定向到成功页面
        
        # 验证项目已创建
        project = Project.objects.get(title='New Test Project')
        self.assertEqual(project.description, 'A new test project')
        self.assertEqual(project.project_category, 'DEVELOPMENT')
        self.assertEqual(project.client_name, 'Test Client')
    
    def test_project_update_workflow(self):
        """测试项目更新工作流"""
        project = ProjectFactory()
        
        update_data = {
            'title': 'Updated Project Title',
            'description': 'Updated description',
            'project_category': 'TESTING',
            'client_name': 'Updated Client',
            'budget': '7500.00',
        }
        
        response = self.client.post(
            reverse('projects:project_update', args=[project.pk]), 
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 验证更新
        updated_project = Project.objects.get(pk=project.pk)
        self.assertEqual(updated_project.title, 'Updated Project Title')
        self.assertEqual(updated_project.project_category, 'TESTING')
    
    def test_project_delete_workflow(self):
        """测试项目删除工作流"""
        project = ProjectFactory()
        
        response = self.client.post(reverse('projects:project_delete', args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        
        # 验证删除
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())


class TaskIntegrationTest(TestCase):
    """Task集成测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
        self.project = ProjectFactory()
        self.client.force_login(self.user)
    
    def test_task_create_workflow(self):
        """测试任务创建工作流"""
        task_data = {
            'title': 'New Test Task',
            'description': 'A new test task',
            'priority': 'HIGH',
            'status': 'TODO',
            'project': self.project.pk,
        }
        
        response = self.client.post(reverse('projects:task_create'), task_data)
        self.assertEqual(response.status_code, 302)
        
        # 验证任务已创建
        task = Task.objects.get(title='New Test Task')
        self.assertEqual(task.description, 'A new test task')
        self.assertEqual(task.priority, 'HIGH')
        self.assertEqual(task.status, 'TODO')
        self.assertEqual(task.project, self.project)
    
    def test_task_update_workflow(self):
        """测试任务更新工作流"""
        task = TaskFactory(project=self.project, created_by=self.userprofile)
        
        update_data = {
            'title': 'Updated Task Title',
            'description': 'Updated task description',
            'priority': 'MEDIUM',
            'status': 'IN_PROGRESS',
            'project': self.project.pk,
        }
        
        response = self.client.post(
            reverse('projects:task_update', args=[task.pk]), 
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 验证更新
        updated_task = Task.objects.get(pk=task.pk)
        self.assertEqual(updated_task.title, 'Updated Task Title')
        self.assertEqual(updated_task.status, 'IN_PROGRESS')
    
    def test_task_delete_workflow(self):
        """测试任务删除工作流"""
        task = TaskFactory(project=self.project, created_by=self.userprofile)
        
        response = self.client.post(reverse('projects:task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        
        # 验证删除
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())


class ProjectDataTest(TestCase):
    """Project数据测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.projects = []
        for i in range(5):
            project = ProjectFactory()
            self.projects.append(project)
    
    def test_project_data_integrity(self):
        """测试数据完整性"""
        for project in self.projects:
            self.assertIsNotNone(project.title)
            self.assertIsNotNone(project.project_category)
            self.assertIn(project.project_category, dict(Project.PROJECT_CATEGORY_CHOICES))
            self.assertIsNotNone(project.created_at)
            self.assertIsNotNone(project.updated_at)
    
    def test_project_unique_title_constraint(self):
        """测试标题唯一性约束"""
        project = self.projects[0]
        with self.assertRaises(Exception):
            Project.objects.create(title=project.title)
    
    def test_project_cascade_delete(self):
        """测试级联删除"""
        project = self.projects[0]
        task = TaskFactory(project=project)
        
        # 删除项目
        project.delete()
        
        # 相关任务应该也被删除
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
    
    def test_project_bulk_operations(self):
        """测试批量操作"""
        # 批量更新
        Project.objects.filter(project_category='EXPLORING').update(
            project_category='DEVELOPMENT'
        )
        
        # 验证更新
        updated_count = Project.objects.filter(project_category='DEVELOPMENT').count()
        self.assertGreater(updated_count, 0)
        
        # 批量查询
        exploring_projects = Project.objects.filter(project_category='EXPLORING')
        development_projects = Project.objects.filter(project_category='DEVELOPMENT')
        
        self.assertIsNotNone(exploring_projects)
        self.assertIsNotNone(development_projects)


class TaskDataTest(TestCase):
    """Task数据测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.userprofile = UserProfileFactory()
        self.project = ProjectFactory()
        self.tasks = []
        for i in range(5):
            task = TaskFactory(project=self.project, created_by=self.userprofile)
            self.tasks.append(task)
    
    def test_task_data_integrity(self):
        """测试数据完整性"""
        for task in self.tasks:
            self.assertIsNotNone(task.title)
            self.assertIsNotNone(task.project)
            self.assertIsNotNone(task.priority)
            self.assertIn(task.priority, dict(Task.PRIORITY_CHOICES))
            self.assertIsNotNone(task.status)
            self.assertIn(task.status, dict(Task.STATUS_CHOICES))
            self.assertIsNotNone(task.created_at)
            self.assertIsNotNone(task.updated_at)
    
    def test_task_foreign_key_constraints(self):
        """测试外键约束"""
        task = self.tasks[0]
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.created_by, self.userprofile)
    
    def test_task_status_transitions(self):
        """测试状态转换"""
        task = self.tasks[0]
        
        # TODO -> IN_PROGRESS
        task.status = 'IN_PROGRESS'
        task.save()
        self.assertEqual(task.status, 'IN_PROGRESS')
        self.assertEqual(task.progress_percentage, 50)
        
        # IN_PROGRESS -> REVIEW
        task.status = 'REVIEW'
        task.save()
        self.assertEqual(task.status, 'REVIEW')
        self.assertEqual(task.progress_percentage, 75)
        
        # REVIEW -> COMPLETED
        task.status = 'COMPLETED'
        task.save()
        self.assertEqual(task.status, 'COMPLETED')
        self.assertEqual(task.progress_percentage, 100)
    
    def test_task_priority_impact(self):
        """测试优先级影响"""
        high_priority_task = TaskFactory(project=self.project, priority='HIGH')
        low_priority_task = TaskFactory(project=self.project, priority='LOW')
        
        tasks = Task.objects.filter(project=self.project).order_by('-priority')
        self.assertEqual(tasks[0], high_priority_task)
        self.assertEqual(tasks[-1], low_priority_task)
    
    def test_task_overdue_calculation(self):
        """测试过期计算"""
        # 过期任务
        overdue_task = TaskFactory(
            project=self.project,
            due_date=timezone.now() - timezone.timedelta(days=1),
            completed=False
        )
        self.assertTrue(overdue_task.is_overdue)
        
        # 未过期任务
        future_task = TaskFactory(
            project=self.project,
            due_date=timezone.now() + timezone.timedelta(days=1),
            completed=False
        )
        self.assertFalse(future_task.is_overdue)
        
        # 已完成任务（即使过期也不算过期）
        completed_overdue_task = TaskFactory(
            project=self.project,
            due_date=timezone.now() - timezone.timedelta(days=1),
            completed=True
        )
        self.assertFalse(completed_overdue_task.is_overdue)
