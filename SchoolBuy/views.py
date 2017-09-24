#coding=utf8
# Create your views here.

import datetime,os,random,math,base64
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.http import HttpResponse,Http404
from django.shortcuts import render
from django.conf import settings
from django.contrib import auth
from SchoolBuy.shuju import *
from io import BytesIO
from SchoolBuy.forms import *
from comm.comm_method import filetype,creat_head,create_code,creat_small_img



def create_code_img(request):
    #在内存中开辟空间用以生成临时的图片
    f = BytesIO()
    img,code = create_code()
    request.session['check_code'] = code
    img.save(f,'PNG')
    return HttpResponse(f.getvalue(),content_type="image/png")

def home(request):

    return render(request, 'SchoolBuy/index.html')

#注册
def register(request):
    code_err = False
    if request.method == 'POST':
        form = Register(request.POST)

        if request.POST.get('code',' ') != request.session.get('check_code',None):
            code_err = True

        else:
            if form.is_valid():  # 判断是否合法
                user = User.objects.create_user(username=form.cleaned_data['username']
                                                ,password=form.cleaned_data['passwd'])
                user.date_joined = datetime.datetime.now()
                user.save()
                all_user = UserProfile()
                all_user.User = user
                all_user.Nick = user.username
                all_user.save()
                send_mail('用户注册',
                          '用户名：'+form.cleaned_data['username']+'\n密码：'+form.cleaned_data['passwd'],
                          settings.DEFAULT_FROM_EMAIL,
                         [settings.ADMIN_EMAIL,], fail_silently=False)
                return HttpResponseRedirect('/')
    else:
        form = Register()
    return render(request, 'SchoolBuy/Register.html', {'form': form,'code_err':code_err})

#登录
def login(request):
    if request.method == 'POST':
        name = request.POST.get('username','')
        passwd = request.POST.get('password','')
        user = auth.authenticate(username=name,password=passwd)
        if user is not None and user.is_active:
            auth.login(request,user)
            profile = UserProfile.objects.get(User=user)
            request.session['nick'] = profile.Nick
            request.session['avatar'] = profile.Avatar
            return HttpResponseRedirect('/')

        else:
            return render(request,'SchoolBuy/Login.html',{'error':'用户名和密码不匹配！'})

    else:
        return render(request,'SchoolBuy/Login.html')

#注销
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def save2images(file,goodsmessage):
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'images')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'images'))
    full_path = os.path.join(settings.MEDIA_ROOT, 'images' , file.name)
    file_name = file.name
    if(os.path.exists(full_path)):
        #新文件名添加了16位随机字符
        file_name = file_name[:-len(file_name.split('.')[-1]) - 1] + '_' + \
                   ''.join(random.sample(string.ascii_letters + string.digits, 16)) + \
                   '.' + file_name.split('.')[-1]
        full_path = os.path.join(settings.MEDIA_ROOT, 'images' , file_name)
    fd = open(full_path,'wb+')
    for chunks in file.chunks():
        fd.write(chunks)
    fd.close()
    if(filetype(full_path) == 'unknown'):
        os.remove(full_path)
        return None
    #进行图片剪裁
    sm_img = creat_small_img(full_path)
    big_img = creat_small_img(full_path,'big')
    if big_img:
        os.remove(full_path)
    else:
        big_img = os.path.join('/media/images',os.path.basename(full_path))
    g = GoodsImage(ImgBig=big_img,ImgSma=sm_img)
    g.save()
    goodsmessage.Images.add(g)

    #如果无图就添加一张新图
    if not goodsmessage.First_pic:
        goodsmessage.First_pic = g
        goodsmessage.save()



@login_required
def push_goods(request):

    f = GoodsForm()
    code_err = False
    if request.method == 'POST':

        f = GoodsForm(request.POST,request.FILES)

        if request.POST.get('code',' ') != request.session.get('check_code',None):
            code_err = True

        else:
            if f.is_valid():

                e_f = f.save(commit=False)
                e_f.Ctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                e_f.Mtime = e_f.Ctime
                e_f.Owner = request.user
                e_f.save()

                # 获取上传文件列表
                f = request.FILES.getlist('image')

                if(f):
                    good = GoodsMessage.objects.get(id = e_f.id)
                    for p in f:
                        save2images(p,good)

                return HttpResponseRedirect('/goods/'+str(e_f.id))

    return render(request, 'SchoolBuy/PushGoods.html',{'form':f,'code_err':code_err})

#查看商品具体信息
def look_goods(request,number):
    goods = GoodsMessage.objects.filter(id = number).first()

    if(goods):
        profile = UserProfile.objects.get(User=goods.Owner)
        #增加访问量
        goods.PV = goods.PV + 1
        goods.save()
        #抓取图片
        image = goods.Images.all()
        #抓取回复
        words = GoodsWords.objects.filter(Owner=goods,Display=True)

        user = request.user

        f = GoodsWordsForm()
        return render(request,'SchoolBuy/GoodsMessage.html',{'uid':user.id,'words':words,'form':f,'profile':profile,'goods':goods,'image':image})
    else:
        raise Http404()

def return_page_list(max,now,each):

    offset = each//2
    if max<=each:
        list = range(1,max+1)
    else:
        if now-offset > 0 and now+offset<=max:
            list = range(now-offset,now+offset+1)
        elif now-offset > 0 and now+offset>max:
            list = range(max-offset*2,max+1)
        else :
            list = range(1,2+offset*2)
    return list


#所有商品
@csrf_exempt
def goods_list(request):
    str = ''
    each = 1  # 每页显示数量
    list_page = 5  # 一共显示多少个链接页 偶数会+1
    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except:
        raise Http404()
    start = (page-1) * each
    end = page * each
    goods = GoodsMessage.objects.filter(Is_alive=True)
    form = SearchForm(request.GET)
    if form.is_valid():
        name = form.cleaned_data['name']
        type = form.cleaned_data['type']
        if name:
            str = str+'&name='+request.GET.get('name')
            goods = goods.filter(Title__contains=name)
        if type:
            str = str + '&type='+request.GET.get('type')
            goods = goods.filter(Category = type)
    max = goods.count()
    goods = goods[start:end]
    if not goods:
        return render(request, "SchoolBuy/No_Goods.html")
    lastpage = math.ceil(max*1.0 / each)  #统一python2
    pg = pagiton()
    pg.list = return_page_list(lastpage,page,list_page)
    pg.now = page
    if page == 1 :
        pg.hasHead = False
    if page == lastpage:
        pg.hasEnd = False
    pg.end = lastpage
    pg.canshu = str


    return render(request,'SchoolBuy/GoodsList.html',{'goods':goods,'form':form,'page':pg})


#添加留言推送
def add_push_mess(good,reply,user):
    log = GoodsLog()
    log.Owner = good
    log.From = UserProfile.objects.filter(User=user).first()
    if not reply.To:
        log.To = good.Owner
    else:
        log.To = reply.To.From.User
    log.Mess = reply
    log.save()

@login_required
#发布商品留言
def goods_reply(request):

    #只接受POST
    if request.method != "POST":
        raise Http404()


    f = GoodsWordsForm(request.POST)
    if(f.is_valid()):
        owner = request.POST.get('goods_id',None)
        goods = GoodsMessage.objects.filter(id=owner,Is_alive=True).first()
        # 发表留言所属的商品不存在或已经下架
        if not owner or not goods:
            return HttpResponse("似乎有点问题，重试试吧！")

        reply = GoodsWords()
        reply.Words = f.cleaned_data['Words']
        reply.Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reply.Owner = goods
        reply.From = UserProfile.objects.get(User=request.user)
        to = f.cleaned_data['To']
        #验证回复给的留言是否属于该商品
        t = GoodsWords.objects.filter(id=to,Owner=goods).first()
        if to and t:
            reply.To = t
        reply.save()
        #添加留言推送
        add_push_mess(goods,reply,request.user)
        return HttpResponseRedirect('/goods/'+str(goods.id))
    else:
        return HttpResponse('请正确填写回复内容')


#查看别人信息
def look_user(request,id):
    profile = UserProfile.objects.filter(User=id).first()
    if(not profile):
        raise Http404()
    #不能用values查询,values返回的是字典而不是QuerySet
    goods = GoodsMessage.objects.filter(Is_alive=True,Owner=id)
    return render(request,'SchoolBuy/UserMessage.html', {'profile':profile,'goods': goods})


@login_required
#用户个人信息
def user_message(request):
    user = request.user
    profile = UserProfile.objects.get(User=user)
    #包含下架商品
    goods = GoodsMessage.objects.filter(Owner=user)

    #系统通知个数
    log = len(GoodsLog.objects.filter(To = user,Readed=False))

    return render(request,'SchoolBuy/MyMessage.html', {'log':log,'profile': profile, 'goods': goods})


@login_required
#编辑商品
def edit_goods(request,id):
    type = GoodsType.objects.all()
    user = request.user
    goods = GoodsMessage.objects.filter(id=id,Is_alive=True,Owner=user).first()
    if not goods:
        raise Http404()
    if request.method == 'POST':
        form = GoodsForm(request.POST,instance=goods)
        if form.is_valid():
            e_f = form.save(commit=False)
            e_f.Mtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            e_f.save()
            return HttpResponseRedirect('/edit/'+str(e_f.id))
    else:
        form = GoodsForm(instance=goods)
    pic = goods.Images.all()
    return render(request,'SchoolBuy/Edit.html',{'type':type,'form':form,'image':pic,'id':goods.id})

@login_required
#商品添加图片
def add_pic(request):
    if request.method != 'POST':
        raise Http404()
    id = request.POST.get('goods_id',None)
    goods = GoodsMessage.objects.filter(id = id,Is_alive=True).first()
    if not goods:
        raise Http404()
    f = request.FILES.getlist('image')
    if (f):
        for i in f:
            save2images(i, goods)
    return HttpResponseRedirect("/edit/"+id)

# 删除img的大小两个文件
def img_file_del(image):
    pic = str(image.ImgBig)
    mini = str(image.ImgSma)
    try:
        os.remove(settings.MEDIA_ROOT+'/../'+pic)
        os.remove(settings.MEDIA_ROOT+'/../'+mini)
    except:
        os.remove(settings.MEDIA_ROOT+'/../'+mini)

@login_required
#删除商品图片
def del_pic(request):
    goods_id = request.GET.get('goods_id',None)
    image_id = request.GET.get('image_id',None)
    if(not goods_id or not image_id):
        raise Http404()
    goods = GoodsMessage.objects.filter(id=goods_id,Is_alive=True).first()
    image = goods.Images.filter(id=image_id).first()
    if not image:
        raise Http404()

    #先将第一张图置空，然后重新保存
    goods.First_pic = None
    goods.save()

    #删除商品图片关联
    goods.Images.remove(image)

    #删除磁盘文件
    img_file_del(image)

    #删除商品图片表记录
    image.delete()

    #添加首图
    goods.First_pic = goods.Images.first()
    goods.save()
    return HttpResponseRedirect('/edit/'+goods_id)


@login_required
#删除商品
def del_good(request,id):
    user = request.user
    good = GoodsMessage.objects.filter(id = id).first()
    if not good:
        raise Http404()

    #删除评论

    words = GoodsWords.objects.filter(Owner = good).delete()

    #删除图片
    image = good.Images.all()
    for i in image:
        img_file_del(i)

    image.delete()

    #删除相关提醒
    GoodsLog.objects.filter(Owner=good).delete()

    #删除商品
    good.delete()

    return HttpResponseRedirect("/me/")


@login_required
#删除评论
def del_good_words(request):
    good_id = request.GET.get('good_id',None)
    word_id = request.GET.get('word_id',None)
    good = GoodsMessage.objects.filter(id = good_id).first()
    word = GoodsWords.objects.filter(Owner=good,id=word_id).first()
    if not word:
        raise Http404()
    user = request.user
    if word.From.User == user:
        word.Display = False
        word.save()
        return HttpResponseRedirect('/goods/'+good_id)
    raise Http404()

@login_required
#显示提示
def show_log(request):
    user = request.user
    Newlog = GoodsLog.objects.filter(To=user,Readed=False)
    Oldlog = GoodsLog.objects.filter(To=user,Readed=True)

    return render(request,"SchoolBuy/MyLog.html",{'Newlog':Newlog,'Oldlog':Oldlog})

@login_required
#读消息中转页面
def read_log(request):
    id = request.GET.get('id',None)
    log = GoodsLog.objects.filter(To=request.user,id=id).first()
    if not log:
        raise Http404()

    if log.Readed == False:
        log.Readed = True
        log.save()

    return HttpResponseRedirect('/goods/'+str(log.Owner.id))

@login_required
#消息处理页面 /log/mamager/?method=*&id=*
def log_manager(request):
    def Del_all():
        GoodsLog.objects.filter(To=request.user).delete()

    def Del_old():
        GoodsLog.objects.filter(To=request.user,Readed=True).delete()

    def Read_new():
        logs = GoodsLog.objects.filter(To=request.user,Readed=False)
        for i in logs:
            i.Readed = True
            i.save()

    def Del_each():
        GoodsLog.objects.filter(To=request.user, id=id).delete()


    method = request.GET.get('method', None)
    id = request.GET.get('id', None)

    switcher = {
        'del_all' : Del_all,  # 删除所有消息
        'del_old' : Del_old,  # 删除所有旧消息
        'read_new' : Read_new, # 标记所有为已读
        'del_each' : Del_each  # 删除单条
    }

    end = switcher.get(method,None)
    if end:
        end()
        return HttpResponseRedirect('/me/log/')
    raise Http404()


#保存头像
def savehead(pic):
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'head')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'head'))
    randname = ''.join(random.sample(string.ascii_letters + string.digits, 24))
    randname += '.' + pic.name.split('.')[-1]
    full_path = os.path.join(settings.MEDIA_ROOT, 'head', randname)
    fd = open(full_path, 'wb+')
    for chunks in pic.chunks():
        fd.write(chunks)
    fd.close()
    if (filetype(full_path) == 'unknown'):
        os.remove(full_path)
        return None
    else:
        nn = creat_head(full_path)
        os.remove(full_path)
        return nn



#修改自身信息
@login_required
def change_myself(request):
    pass_form = ChangePasswd()
    email_form = BindEmailForm()
    profile = UserProfile.objects.get(User=request.user)
    if profile.EmailCode:
        temp_email = base64.b64decode(profile.EmailCode[:-24].encode('utf8'))
        email_form = BindEmailForm({'email':temp_email})
        email_form.add_error('email','你在'+profile.EmailCodeTime.strftime('%Y-%m-%d %H:%M:%S')+
                             '提交了邮箱，请在24小时内点击链接激活，并且一小时之内不能再次发送激活邮件')
    if request.method != 'POST':
        form = UserMessage(instance=profile)
    else:
        form = UserMessage(request.POST)
        if form.is_valid():
            profile.Nick = form.cleaned_data['Nick']
            profile.save()
            request.session['nick'] = profile.Nick

            pic = request.FILES.get('Avatar')
            if pic:
                nn = savehead(pic)
                if nn:
                    #非系统图片就删除以前的图片
                    if(str(profile.Avatar)[:6] == '/media'):
                        os.remove(settings.BASE_DIR+str(profile.Avatar))

                    profile.Avatar = nn
                    profile.save()
                    request.session['avatar'] = nn

    return render(request,'SchoolBuy/ChangeMyself.html',
                  {'profile':profile,'form':form,
                   'pass_form':pass_form,'email_form':email_form})

def send_required_mail(mail,profile):
    str = (base64.b64encode(mail.encode('utf8'))).decode('utf8')
    str += ''.join(random.sample(string.ascii_letters + string.digits, 24))
    profile.EmailCode = str
    profile.EmailCodeTime = datetime.datetime.now()
    profile.save()
    url = '请点击这个链接来激活您的邮箱绑定(24小时有效)\n' + settings.HOST_URL_ADDRESS + '/comm/email/?code='+str
    send_mail('邮箱绑定',url,settings.DEFAULT_FROM_EMAIL,[mail,],fail_silently=False)


@login_required
#绑定邮箱
def bind_email(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/me/edit/')

    form = UserMessage()
    pass_form = ChangePasswd()
    profile = UserProfile.objects.get(User=request.user)
    if request.user.email:
        return HttpResponse("error!重复绑定")
    user = request.user
    email_form = BindEmailForm(request.POST)
    if profile.EmailCodeTime and (datetime.datetime.now()-profile.EmailCodeTime).seconds <= 3600:
        email_form.add_error('email','1小时内不能重复发送激活邮件')
        return render(request, 'SchoolBuy/ChangeMyself.html',
                      {'profile': profile, 'form': form,
                       'pass_form': pass_form, 'email_form': email_form})

    else:
        if email_form.is_valid():
            send_required_mail(email_form.cleaned_data['email'],profile)
            return HttpResponseRedirect('/me/edit/')

        return render(request, 'SchoolBuy/ChangeMyself.html',
                      {'profile': profile, 'form': form,
                       'pass_form': pass_form, 'email_form': email_form})








@login_required
#修改密码
def change_passwd(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/me/edit/')
    else:
        profile = UserProfile.objects.get(User=request.user)
        form = UserMessage(instance=profile)
        pass_form = ChangePasswd(request.POST)
        passwd = request.POST.get('old_passwd',None)
        name = request.user.username
        user = auth.authenticate(username=name,password=passwd)
        if not user:
            pass_form.add_error('old_passwd','原密码错误！')
            return render(request, 'SchoolBuy/ChangeMyself.html', {'profile': profile, 'form': form,'pass_form':pass_form})
        if pass_form.is_valid():
            user.set_password(pass_form.cleaned_data['new_passwd'])
            user.save()
            auth.logout(request)
            request.session.clear()
            return render(request, "SchoolBuy/doing_success.html", {'mes': '修改密码'})
    return render(request, 'SchoolBuy/ChangeMyself.html', {'profile': profile, 'form': form, 'pass_form': pass_form})

@csrf_exempt
def verifi_email(request):
    code = request.GET.get('code',None)
    code = UserProfile.objects.filter(EmailCode=code).first()
    if not code:
        raise Http404()
    if (datetime.datetime.now()-code.EmailCodeTime).seconds >= 3600*24:
        return HttpResponse('验证链接已经过期，请重新生成！')
    else:
        user = code.User
        temp_email = base64.b64decode(code.EmailCode[:-24].encode('utf8'))
        user.email = temp_email
        user.save()
        code.EmailCode = None
        code.EmailCodeTime = None
        code.save()
        return HttpResponse('激活成功！')

@login_required
def del_email(request):
    user = request.user
    user.email=''
    user.save()
    return HttpResponseRedirect('/me/edit/')

def send_passwd_mail(mail,profile):
    str = (base64.b64encode(mail.encode('utf8'))).decode('utf8')
    str += ''.join(random.sample(string.ascii_letters + string.digits, 24))
    profile.PasswdCode = str
    profile.PasswdCodeTime = datetime.datetime.now()
    profile.save()
    url = '请点击这个链接来重新设定您的密码(24小时内有效)\n' + settings.HOST_URL_ADDRESS + '/comm/passwd/?code='+str
    send_mail('重置密码',url,settings.DEFAULT_FROM_EMAIL,[mail,],fail_silently=False)

#输入邮箱找回密码
def find_passwd(request):
    if request.method == 'GET':
        form = FindPasswdForm()

    else:
        form = FindPasswdForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            profile = UserProfile.objects.get(User = user)
            if profile.PasswdCodeTime and (datetime.datetime.now() - profile.PasswdCodeTime).seconds <= 1800 :
                form.add_error('email','已于'+profile.PasswdCodeTime.strftime('%Y-%m-%d %H:%M:%S')+
                               '发送了重置邮件，半小时内无法再次发送')

            else:
                send_passwd_mail(form.cleaned_data['email'],profile)
                return HttpResponse('已向你发送了重置密码链接，快去邮箱查看吧！')
    return render(request,'SchoolBuy/ForgetPasswd.html',{'form':form})

#重置密码
def reset_passwd(request):
    if request.method == 'GET':
        code = request.GET.get('code',None)
        profile = UserProfile.objects.filter(PasswdCode = code).first()
        if profile and (datetime.datetime.now()-profile.PasswdCodeTime).seconds <= 3600*24:
            form = ResetPasswdForm({'code':code})
            return render(request,"SchoolBuy/ResetPasswd.html",{'form':form})
        else:
            return HttpResponse("链接已过期或不存在！")
    else:
        code = request.POST.get('code',None)
        profile = UserProfile.objects.filter(PasswdCode=code).first()
        if profile and (datetime.datetime.now() - profile.PasswdCodeTime).seconds <= 3600 * 24:
            form = ResetPasswdForm(request.POST)
            if form.is_valid():
                user = profile.User
                user.set_password(form.cleaned_data['new_passwd'])
                user.save()
                profile.PasswdCode = None
                profile.PasswdCodeTime = None
                profile.save()
                return render(request, "SchoolBuy/doing_success.html", {'mes': '重置密码'})
            else:
                return render(request,'SchoolBuy/ResetPasswd.html',{'form':form})
        else:
            return HttpResponse("链接已过期或不存在！")
