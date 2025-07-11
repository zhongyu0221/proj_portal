# 测试文档

本项目包含完整的单元测试和集成测试套件，用于确保代码质量和功能正确性。

## 测试结构

### 测试文件
- `userprofiles/tests.py` - UserProfile模型和视图测试
- `project/tests.py` - Project和Task模型、视图、表单测试
- `project/management/commands/generate_test_data.py` - 测试数据生成命令

### 测试类型

#### 1. 模型测试 (Model Tests)
- 测试模型创建、更新、删除
- 测试模型方法、属性、约束
- 测试数据完整性

#### 2. 视图测试 (View Tests)
- 测试视图响应状态
- 测试视图内容
- 测试权限控制

#### 3. 表单测试 (Form Tests)
- 测试表单验证
- 测试有效和无效数据
- 测试表单保存

#### 4. 集成测试 (Integration Tests)
- 测试完整工作流
- 测试用户交互
- 测试数据流

## 运行测试

### 1. 使用Django测试命令

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test userprofiles
python manage.py test project

# 运行特定测试类
python manage.py test userprofiles.tests.UserProfileModelTest
python manage.py test project.tests.ProjectModelTest

# 运行特定测试方法
python manage.py test userprofiles.tests.UserProfileModelTest.test_userprofile_creation
```

### 2. 使用pytest (推荐)

```bash
# 安装pytest和pytest-django
pip install pytest pytest-django

# 运行所有测试
pytest

# 运行特定测试
pytest userprofiles/tests.py
pytest project/tests.py

# 运行特定测试类
pytest userprofiles/tests.py::UserProfileModelTest
pytest project/tests.py::ProjectModelTest

# 运行特定测试方法
pytest userprofiles/tests.py::UserProfileModelTest::test_userprofile_creation

# 运行标记的测试
pytest -m "model"
pytest -m "view"
pytest -m "integration"
```

### 3. 使用测试运行脚本

```bash
# 运行所有测试
python run_tests.py

# 运行特定测试
python run_tests.py --specific
```

## 生成测试数据

### 使用管理命令

```bash
# 生成默认测试数据 (10用户, 20项目, 50任务, 15问题)
python manage.py generate_test_data

# 生成自定义数量的测试数据
python manage.py generate_test_data --users 20 --projects 30 --tasks 100 --issues 25

# 清除现有数据并生成新数据
python manage.py generate_test_data --clear

# 只生成少量数据用于快速测试
python manage.py generate_test_data --users 5 --projects 10 --tasks 20 --issues 5
```

### 测试数据内容

#### 用户数据
- 用户名: user1, user2, ...
- 密码: testpass123
- 用户级别: Technologist, Manager, Director, Super Admin
- 随机城市和电话号码

#### 项目数据
- 项目标题: "Project X: [类型]"
- 项目类别: Exploring, Research, Development, Testing, Deployment, Maintenance, Other
- 随机预算、客户名称、截止日期

#### 任务数据
- 任务标题: "Task X: [活动]"
- 优先级: Low, Medium, High, Urgent
- 状态: To Do, In Progress, Review, Completed, Cancelled
- 随机到期日期和完成状态

#### 问题数据
- 问题描述: "Issue X: [问题类型]"
- 类别: Product Design, Development, QA & Testing, Customer Queries, R & D
- 状态历史记录

## 测试覆盖率

### 安装覆盖率工具

```bash
pip install coverage
```

### 运行覆盖率测试

```bash
# 运行测试并生成覆盖率报告
coverage run --source='.' manage.py test
coverage report
coverage html  # 生成HTML报告
```

## 测试最佳实践

### 1. 测试命名
- 测试方法名应该清晰描述测试内容
- 使用描述性的测试类名
- 添加详细的文档字符串

### 2. 测试数据
- 使用Factory Boy创建测试数据
- 避免硬编码测试数据
- 使用随机数据增加测试覆盖

### 3. 测试隔离
- 每个测试应该是独立的
- 使用setUp和tearDown方法
- 避免测试间的依赖

### 4. 测试断言
- 使用具体的断言方法
- 测试边界条件
- 测试异常情况

### 5. 性能测试
- 标记慢速测试: `@pytest.mark.slow`
- 使用数据库事务回滚
- 避免不必要的数据库查询

## 常见问题

### 1. 数据库问题
```bash
# 如果遇到数据库问题，重新创建测试数据库
python manage.py test --keepdb
```

### 2. 导入错误
确保所有必要的包都已安装：
```bash
pip install factory-boy faker
```

### 3. 测试失败
- 检查测试数据是否正确
- 验证模型约束
- 确认URL配置正确

## 持续集成

### GitHub Actions配置示例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-django factory-boy faker
    - name: Run tests
      run: |
        python manage.py test
```

## 测试维护

### 添加新测试
1. 在相应的tests.py文件中添加测试类
2. 使用适当的测试标记
3. 添加详细的文档字符串
4. 确保测试覆盖新功能

### 更新现有测试
1. 当模型或视图发生变化时更新测试
2. 保持测试数据的真实性
3. 定期运行测试确保没有回归

### 测试文档
- 保持此文档的更新
- 记录测试策略和决策
- 分享测试最佳实践 