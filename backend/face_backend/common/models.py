from django.db import models
import datetime
# Create your models here.
class Event(models.Model):
    # 创建日期 缺省设计
    time = models.DateTimeField(default=datetime.datetime.now)
    # 用户名
    username = models.CharField(max_length=200)

    # 年龄段
    age = models.CharField(max_length=200)

    # 性别
    gender = models.CharField(max_length=200)
    # 表情
    expression = models.CharField(max_length=200)
