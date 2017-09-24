#coding=utf8

import struct
import random,string,os
from django.conf import settings
from PIL import Image,ImageDraw,ImageFont,ImageFilter

#生成随机字符串
def getRandomChar():
    #string模块包含各种字符串，以下为小写字母加数字
    ran = string.ascii_lowercase+string.digits
    char = ''
    for i in range(4):
        char += random.choice(ran)
    return char

#返回一个随机的RGB颜色
def getRandomColor():
    return (random.randint(50,150),random.randint(50,150),random.randint(50,150))

def create_code():

    #创建图片，模式，大小，背景色
    img = Image.new('RGB', (120,30), (255,255,255))
    #创建画布
    draw = ImageDraw.Draw(img)
    #设置字体
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR,'comm/Arial.ttf'), 25)

    code = getRandomChar()
    #将生成的字符画在画布上
    for t in range(4):
        draw.text((30*t+5,0),code[t],getRandomColor(),font)

    #生成干扰点
    for _ in range(random.randint(0,50)):
        #位置，颜色
        draw.point((random.randint(0, 120), random.randint(0, 30)),fill=getRandomColor())

    #使用模糊滤镜使图片模糊
    img = img.filter(ImageFilter.BLUR)
    #保存
    #img.save(''.join(code)+'.jpg','jpeg')
    return img,code


# 支持文件类型
# 用16进制字符串的目的是可以知道文件头是多少字节
# 各种文件头的长度不一样，少半2字符，长则8字符
def typeList():
    return {
        'FFD8FF':'IMG_JPEG',
        '89504E47':'IMG_PNG',
    }


# 字节码转16进制字符串
def bytes2hex(bytes):
    num = len(bytes)
    hexstr = u""
    for i in range(num):
        t = u"%x" % bytes[i]
        if len(t) % 2:
            hexstr += u"0"
        hexstr += t
    return hexstr.upper()


# 获取文件类型
def filetype(filename):
    binfile = open(filename, 'rb')  # 必需二制字读取
    tl = typeList()
    ftype = 'unknown'
    for hcode in tl.keys():
        numOfBytes = len(hcode) // 2  # 需要读多少字节
        binfile.seek(0)  # 每次读取都要回到文件头，不然会一直往后读取
        hbytes = struct.unpack_from('B' * numOfBytes, binfile.read(numOfBytes))  # 一个 "B"表示一个字节
        f_hcode = bytes2hex(hbytes)
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    binfile.close()
    return ftype

#生成小头像
def creat_head(path):
    name = ''.join(random.sample(string.ascii_letters + string.digits, 24))+'.png'
    img = Image.open(path)
    small = min(img.size)
    box = ((img.size[0]-small)/2,(img.size[1]-small),(img.size[0]-small)/2 + small,(img.size[1]-small)/2 + small)
    # 裁切图片
    cropImg = img.crop(box)
    # 缩略图
    cropImg.thumbnail((50,50), Image.ANTIALIAS)
    cropImg.save(os.path.join(settings.MEDIA_ROOT,'head',name))
    return os.path.join('/media','head',name)


#根据图片生成缩略图，默认小图
def creat_small_img(path,type = 'smale'):
    #缩略图大小
    def_sm_size = (200,200)
    #原图最大一边的长
    max_len = 1366

    #获取文件名
    file_name = os.path.basename(path)
    if type=='smale':
        name = file_name + '.small.png'
        img = Image.open(path)
        small = min(img.size)
        box = ((img.size[0]-small)/2,(img.size[1]-small),(img.size[0]-small)/2 + small,(img.size[1]-small)/2 + small)
        # 裁切图片
        cropImg = img.crop(box)
        # 缩略图
        cropImg.thumbnail(def_sm_size, Image.ANTIALIAS)
        cropImg.save(os.path.join(settings.MEDIA_ROOT,'images',name))
        return os.path.join('/media','images',name)
    else:
        img = Image.open(path)
        big_size = max(img.size)
        if big_size > max_len:
            name = file_name+'.big.png'
            beishu = max_len*1.0 / big_size
            ss = (int(img.size[0]*beishu),int(img.size[1]*beishu))
            img.thumbnail(ss, Image.ANTIALIAS)
            img.save(os.path.join(settings.MEDIA_ROOT, 'images', name))
            return os.path.join('/media', 'images', name)

        else:
            return False
