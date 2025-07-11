#!/bin/bash

# 激活虚拟环境（如果存在）
if [ -d "proj" ]; then
    source proj/bin/activate
fi

# 进入 Django 项目目录
cd proj_management

# 运行数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver 127.0.0.1:8000 