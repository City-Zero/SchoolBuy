from django.db import models
#coding=utf8
# Create your models here.
from django.contrib.auth.admin import User
from django.db import models
#from easy_thumbnails.fields import ThumbnailerImageField
from mptt.models import MPTTModel
from django import forms

#用户基本信息
class UserProfile(models.Model):
    User = models.OneToOneField(User)
    Nick = models.CharField(max_length=255)
    Avatar = models.CharField(max_length=200,default='/static/SchoolBuy/images/logo.png',blank=True,null=True)
    EmailCode = models.CharField(max_length=500,blank=True,null=True)  # 邮箱验证码
    EmailCodeTime = models.DateTimeField(blank=True,null=True)  # 发送验证邮箱的时间（控制用户刷邮件）
    PasswdCode = models.CharField(max_length=500,blank=True,null=True)  # 找回密码验证码
    PasswdCodeTime = models.DateTimeField(blank=True,null=True)  # 发送验证邮箱的时间（控制用户刷邮件）


    def __str__(self):
        return self.User.username


#商品类型
class GoodsType(MPTTModel):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey("self", blank=True, null=True, related_name="children")

    class MPTTMeta:
        parent_attr = 'parent'

    def __str__(self):
        return self.name

class GoodsImage(models.Model):
    ImgBig = models.ImageField(upload_to='images/',blank=True)
    ImgSma = models.ImageField(upload_to='images/',blank=True)

class GoodsMessage(models.Model):
    Title = models.CharField(max_length=20)  # 商品标题
    Category = models.ForeignKey(GoodsType,null=True,blank=True)  # 商品标签
    Details = models.TextField()  # 商品详细描述
    Ctime = models.DateTimeField()  # 发布日期
    Mtime = models.DateTimeField()  # 上次编辑时间
    PV = models.IntegerField(default=0)  # 访问量
    Owner = models.ForeignKey(User)  # 发布者
    Images = models.ManyToManyField(GoodsImage)  # 商品图片
    Is_alive = models.BooleanField(default=True)  # 商品是否上架
    First_pic = models.ForeignKey(GoodsImage,related_name='first_pic',null=True,blank=True,default=None)  # 商品第一张图片，便于使用分页模块查找

    def __str__(self):
        return self.Title + self.Category.name

#留言功能
class GoodsWords(models.Model):
    Owner = models.ForeignKey(GoodsMessage)
    From = models.ForeignKey(UserProfile)  # 来自
    To = models.ForeignKey('self',null=True,blank=True)  #回复给哪条
    Words = models.TextField()
    Display = models.BooleanField(default=True)  # 是否显示
    Time = models.DateTimeField(null=True)


    def __str__(self):
        return self.From.User.username+'->'+self.Words

#通知某人回复了留言
class GoodsLog(models.Model):
    Owner = models.ForeignKey(GoodsMessage)  # 所属商品
    From = models.ForeignKey(UserProfile)  # 来自
    To = models.ForeignKey(User)  # 推送给谁
    Mess = models.ForeignKey(GoodsWords)  #消息内容
    Readed = models.BooleanField(default=False)  #是否已读
