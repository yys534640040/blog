from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

# 用户信息


class User(AbstractUser):
    # 电话号码字段
    # unique 手机号
    mobile = models.CharField(max_length=11, unique=True, blank=True, verbose_name='手机号')

    # 头像
    # upload_to为保存到响应的子目录中
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)

    # 个人简介
    user_desc = models.TextField(max_length=500, blank=True)

    # 修改认证的字段手机号
    USERNAME_FIELD = 'mobile'

    # 创建超级管理员的需要必须输入的字段(不包活手机号和密码)
    REQUIRED_FIELDS = ['username', 'email']
    # 昵称
    nickname = models.CharField(max_length=20, default='', blank=True, verbose_name='昵称')

    # 内部类 class Meta 用于给 model 定义元数据
    class Meta:
        db_table = 'tb_users'  # 修改默认的表名
        verbose_name = '用户管理'  # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.mobile

    def get_nickname(self):
        # 判断nikename是否存在
        if User.objects.filter(mobile=self).exists():
            username = User.objects.get(mobile=self)

            if username.nickname:
                return username.nickname
            else:
                return self.mobile



# def has_nickname(self):
#     return User.objects.filter(mobile=self).exists()


# User.get_nickname = get_nickname


