#coding=utf8

from django.conf.urls import url
from SchoolBuy.views import *

urlpatterns = (url(r'^create_code/$',create_code_img),  # 生成验证码
               url(r'^$', home),
               url(r'^register/$', register),  # 注册
               url(r'^login/$', login),  # 登录
               url(r'^logout/$', logout),  # 登出
               url(r'^push_goods/$', push_goods),  #发布商品
               url(r'^goods/(?P<number>\d+)/$',look_goods),  # 浏览id商品
               url(r'^all/$',goods_list),  # 浏览所有商品
               url(r'^goods/reply/$', goods_reply),  # 发布商品回复
               url(r'^user/(?P<id>\d+)/$', look_user),  # 用户主页
               url(r'^me/$', user_message),  # 我的主页
               url(r'^edit/(?P<id>\d+)/$', edit_goods),  # 编辑物品
               url(r'^add/pic/$', add_pic),  # 添加图片
               url(r'^del/pic/$', del_pic),  # 删除图片
               url(r'^del/good/(?P<id>\d+)/$', del_good),  # 删除物品
               url(r'^del/word/$', del_good_words),  # 删除留言
               url(r'^me/log/$', show_log),  # 查看我的提醒
               url(r'^log/read/$', read_log),  # 读取提醒中转页面
               url(r'^log/manager/$', log_manager),  # 提醒操作
               url(r'^me/edit/$', change_myself),  # 修改用户信息
               url(r'^me/edit/passwd/$',change_passwd),  # 修改密码
               url(r'^me/edit/email/$',bind_email),  # 请求绑定邮箱
               url(r'^comm/email/$',verifi_email),  # 验证邮箱
               url(r'^me/del/email/$',del_email),  # 邮箱解绑
               url(r'^comm/forgetpasswd/$',find_passwd),  # 忘记密码
               url(r'^comm/passwd/$',reset_passwd),  # 点击邮件链接重置密码
               )