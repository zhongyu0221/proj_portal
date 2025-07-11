from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import UserProfile
from .forms import UserProfileForm
import factory
from factory.django import DjangoModelFactory
from factory import Faker
from decimal import Decimal


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


class UserProfileModelTest(TestCase):
    """UserProfile模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
    
    def test_userprofile_creation(self):
        """测试UserProfile创建"""
        self.assertEqual(self.userprofile.user, self.user)
        self.assertIsNotNone(self.userprofile.phone)
        self.assertIsNotNone(self.userprofile.city)
        self.assertEqual(self.userprofile.user_level, UserProfile.TECHNOLOGIST)
    
    def test_userprofile_str_method(self):
        """测试__str__方法"""
        expected_name = self.user.get_full_name()
        self.assertEqual(str(self.userprofile), expected_name)
    
    def test_userprofile_last_name_property(self):
        """测试last_name属性"""
        self.assertEqual(self.userprofile.last_name, self.user.last_name)
    
    def test_userprofile_get_full_name(self):
        """测试get_full_name方法"""
        expected_name = self.user.get_full_name()
        self.assertEqual(self.userprofile.get_full_name(), expected_name)
    
    def test_userprofile_meta_ordering(self):
        """测试Meta排序"""
        user2 = UserFactory(first_name='Alice', last_name='Adams')
        userprofile2 = UserProfileFactory(user=user2)
        
        user3 = UserFactory(first_name='Bob', last_name='Brown')
        userprofile3 = UserProfileFactory(user=user3)
        
        profiles = UserProfile.objects.all()
        self.assertEqual(profiles[0], userprofile2)  # Adams
        self.assertEqual(profiles[1], userprofile3)  # Brown
        self.assertEqual(profiles[2], self.userprofile)  # 原始用户
    
    def test_user_level_choices(self):
        """测试用户级别选择"""
        self.userprofile.user_level = UserProfile.MANAGER
        self.userprofile.save()
        self.assertEqual(self.userprofile.user_level, UserProfile.MANAGER)
        
        self.userprofile.user_level = UserProfile.DIRECTOR
        self.userprofile.save()
        self.assertEqual(self.userprofile.user_level, UserProfile.DIRECTOR)
        
        self.userprofile.user_level = UserProfile.SUPERADMIN
        self.userprofile.save()
        self.assertEqual(self.userprofile.user_level, UserProfile.SUPERADMIN)


class UserProfileViewTest(TestCase):
    """UserProfile视图测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.admin_userprofile = UserProfileFactory(user=self.admin_user)
    
    def test_userprofile_list_view(self):
        """测试用户列表视图"""
        # 未登录用户应该被重定向
        response = self.client.get(reverse('userprofiles:userprofile_list'))
        self.assertEqual(response.status_code, 302)
        
        # 登录用户应该能访问
        self.client.force_login(self.user)
        response = self.client.get(reverse('userprofiles:userprofile_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.userprofile.user.get_full_name())
    
    def test_userprofile_detail_view(self):
        """测试用户详情视图"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('userprofiles:userprofile_detail', args=[self.userprofile.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.userprofile.user.get_full_name())
    
    def test_userprofile_create_view(self):
        """测试用户创建视图"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('userprofiles:userprofile_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_userprofile_update_view(self):
        """测试用户更新视图"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('userprofiles:userprofile_update', args=[self.userprofile.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_userprofile_delete_view(self):
        """测试用户删除视图"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('userprofiles:userprofile_delete', args=[self.userprofile.pk]))
        self.assertEqual(response.status_code, 200)


class UserProfileFormTest(TestCase):
    """UserProfile表单测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)
    
    def test_userprofile_form_valid(self):
        """测试有效表单数据"""
        form_data = {
            'phone': '+1234567890',
            'city': 'New York',
            'user_level': UserProfile.MANAGER,
        }
        form = UserProfileForm(data=form_data, instance=self.userprofile)
        self.assertTrue(form.is_valid())
    
    def test_userprofile_form_invalid(self):
        """测试无效表单数据"""
        form_data = {
            'phone': 'invalid_phone',
            'city': 'A' * 100,  # 超过最大长度
            'user_level': 'INVALID',
        }
        form = UserProfileForm(data=form_data, instance=self.userprofile)
        self.assertFalse(form.is_valid())
    
    def test_userprofile_form_blank_fields(self):
        """测试空白字段"""
        form_data = {
            'phone': '',
            'city': '',
            'user_level': UserProfile.TECHNOLOGIST,
        }
        form = UserProfileForm(data=form_data, instance=self.userprofile)
        self.assertTrue(form.is_valid())  # 这些字段允许为空


class UserProfileIntegrationTest(TestCase):
    """UserProfile集成测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.admin_userprofile = UserProfileFactory(user=self.admin_user)
        self.client.force_login(self.admin_user)
    
    def test_userprofile_create_workflow(self):
        """测试用户创建工作流"""
        # 创建新用户
        user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        
        # 创建用户
        user = User.objects.create_user(**user_data)
        
        # 创建用户档案
        profile_data = {
            'phone': '+1234567890',
            'city': 'Test City',
            'user_level': UserProfile.TECHNOLOGIST,
        }
        
        userprofile = UserProfile.objects.create(user=user, **profile_data)
        
        # 验证创建
        self.assertEqual(userprofile.user.username, 'testuser')
        self.assertEqual(userprofile.phone, '+1234567890')
        self.assertEqual(userprofile.city, 'Test City')
        self.assertEqual(userprofile.user_level, UserProfile.TECHNOLOGIST)
    
    def test_userprofile_update_workflow(self):
        """测试用户更新工作流"""
        user = UserFactory()
        userprofile = UserProfileFactory(user=user)
        
        # 更新用户档案
        userprofile.phone = '+9876543210'
        userprofile.city = 'Updated City'
        userprofile.user_level = UserProfile.MANAGER
        userprofile.save()
        
        # 验证更新
        updated_profile = UserProfile.objects.get(pk=userprofile.pk)
        self.assertEqual(updated_profile.phone, '+9876543210')
        self.assertEqual(updated_profile.city, 'Updated City')
        self.assertEqual(updated_profile.user_level, UserProfile.MANAGER)
    
    def test_userprofile_delete_workflow(self):
        """测试用户删除工作流"""
        user = UserFactory()
        userprofile = UserProfileFactory(user=user)
        
        # 删除用户档案
        userprofile.delete()
        
        # 验证删除
        self.assertFalse(UserProfile.objects.filter(pk=userprofile.pk).exists())
        # 用户应该仍然存在（因为CASCADE关系）
        self.assertTrue(User.objects.filter(pk=user.pk).exists())


class UserProfileDataTest(TestCase):
    """UserProfile数据测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建多个用户档案用于测试
        self.users = []
        self.userprofiles = []
        
        for i in range(5):
            user = UserFactory()
            userprofile = UserProfileFactory(user=user)
            self.users.append(user)
            self.userprofiles.append(userprofile)
    
    def test_userprofile_data_integrity(self):
        """测试数据完整性"""
        for userprofile in self.userprofiles:
            self.assertIsNotNone(userprofile.user)
            self.assertIsNotNone(userprofile.user_level)
            self.assertIn(userprofile.user_level, dict(UserProfile.USER_LEVEL_CHOICES))
    
    def test_userprofile_unique_constraints(self):
        """测试唯一性约束"""
        # 尝试为同一用户创建多个档案应该失败
        user = self.users[0]
        with self.assertRaises(Exception):
            UserProfile.objects.create(user=user, phone='+1234567890')
    
    def test_userprofile_cascade_delete(self):
        """测试级联删除"""
        user = self.users[0]
        userprofile = self.userprofiles[0]
        
        # 删除用户
        user.delete()
        
        # 用户档案应该也被删除
        self.assertFalse(UserProfile.objects.filter(pk=userprofile.pk).exists())
    
    def test_userprofile_bulk_operations(self):
        """测试批量操作"""
        # 批量更新
        UserProfile.objects.filter(user_level=UserProfile.TECHNOLOGIST).update(
            user_level=UserProfile.MANAGER
        )
        
        # 验证更新
        updated_count = UserProfile.objects.filter(user_level=UserProfile.MANAGER).count()
        self.assertGreater(updated_count, 0)
        
        # 批量查询
        technologists = UserProfile.objects.filter(user_level=UserProfile.TECHNOLOGIST)
        managers = UserProfile.objects.filter(user_level=UserProfile.MANAGER)
        
        self.assertIsNotNone(technologists)
        self.assertIsNotNone(managers)
