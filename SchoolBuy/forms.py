#coding=utf8

from django import forms
import string
from django.contrib.auth.admin import User
from django.forms import ModelForm, ModelChoiceField
from SchoolBuy.models import *


#注册
class Register(forms.Form):
    username = forms.CharField(max_length=20,label='用户名')
    passwd = forms.CharField(max_length=20,label='密码',widget=forms.PasswordInput)
    repasswd = forms.CharField(max_length=20,label='重复密码',widget=forms.PasswordInput)



    def clean_username(self):
        viavd = string.digits + string.ascii_letters
        name = self.cleaned_data['username']
        for i in name:
            if i not in viavd:
                raise forms.ValidationError('用户名不合法')
        p = User.objects.only('username').filter(username = name)
        if p:
            raise forms.ValidationError('用户名重复')
        return name


    def clean_repasswd(self):
        passwd = self.cleaned_data.get('passwd')
        repasswd = self.cleaned_data.get('repasswd')
        if passwd != repasswd:
            raise forms.ValidationError('两次密码不一致')
        return repasswd

#发布商品
class GoodsForm(ModelForm):
    #Gategory = ModelChoiceField(queryset=GoodsType.objects.all())  # 不分级单选可
    class Meta:
        model = GoodsMessage
        Gategory = ModelChoiceField(queryset=GoodsType.objects.all())  # 分级单选框
        fields = ['Title','Category','Details']
        labels = {
            'Title': '商品名',
            'Category': '分类',
        }
        widgets = {
            'Title': forms.TextInput(attrs={'class' : 'form-control',
                                            'id' : "inputCount3" ,
                                            'placeholder' : "不要超过20个字",
            }),

            'Gategory' : forms.Select(attrs={'class' : "form-control",

            }),

            'Details' : forms.Textarea(attrs={'class' : "form-control",
                                              'rows' : 3 ,
                                              'id' : "introduction",

            })
        }

class SearchForm(forms.Form):
    name = forms.CharField(max_length=10,label='标题',required=False)
    type = ModelChoiceField(queryset=GoodsType.objects.all(),required=False,label='类型')

class GoodsWordsForm(forms.Form):
    Words = forms.CharField(label='',widget=forms.Textarea(attrs={'rows':3,'cols':50}))
    To = forms.IntegerField(widget=forms.HiddenInput,required=False)



class UserMessage(ModelForm):
    class Meta:
        model=UserProfile
        fields = ['Nick']

        widgets = {
            'Nick': forms.TextInput(attrs={'class': 'form-control',
                                        'id': "inputCount3",
                                        'placeholder': "不要超过20个字",
                                        }),

        }

class ChangePasswd(forms.Form):
    old_passwd = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_passwd = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    re_passwd  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_re_passwd(self):
        passwd = self.cleaned_data.get('new_passwd')
        repasswd = self.cleaned_data.get('re_passwd')
        if passwd != repasswd:
            raise forms.ValidationError('两次密码不一致')
        return repasswd

class BindEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            raise forms.ValidationError(u'这个邮箱已经被别人绑定了')
        return email

class FindPasswdForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if not user:
            raise forms.ValidationError(u'似乎是一个未被注册的邮箱？')
        return email


class ResetPasswdForm(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput())
    new_passwd = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    re_passwd  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


    def clean_re_passwd(self):
        passwd = self.cleaned_data.get('new_passwd')
        repasswd = self.cleaned_data.get('re_passwd')
        if passwd != repasswd:
            raise forms.ValidationError('两次密码不一致')
        return repasswd