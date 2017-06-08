#coding: utf-8
import os
import random
from PIL import Image
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import qrcode

def createNoncestr(length = 32):
    """产生随机字符串，不长于32位"""
    chars = "abcdefghijkmnpqrstuvwxyz23456789"
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)

code_url = 'https://www.yihuangjin.com/gold/invite_friend_add_second?phone=131****7779&promo_token=euqjnc&from=singlemessage&isappinstalled=0'

def generate_qrcode_icon(code_url, img_size = None):

    # version: 调整二维码内节点的浓淡
    # error_correction: 参数控制生成二维的误差 L<7% M<15 Q <15 H<25
    # box_size： 调整二维码的像素点
    # border： 控制默认外边距
    # version = 9 box_size=2 border=4 生成的二维码尺寸为 122 * 122
    qr=qrcode.QRCode(
        version=9,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=2,
        border=4
        )
    qr.add_data(code_url)
    qr.make(fit=True)
    img = qr.make_image()

    # 添加图标
    img = img.convert("RGBA")
    img_w, img_h = img.size
    print img.size
    # 根据img调整icon的尺寸 为img的1／4大小
    factor = 4
    size_w = int(img_w / factor)
    size_h = int(img_h / factor)
    icon = Image.open("/Users/lsy/PycharmProjects/wlb/goldbox-backend/static/pc/imgs/common/logo_2.png")
    icon_w, icon_h = icon.size
    # 使icon尺寸大小为img的1/4
    if icon_w > size_w:
        icon_w = size_w
    if icon_h > size_h:
        icon_h = size_h
    # 把icon变成正方形
    if icon_w > icon_h:
        icon_w = icon_h
    if icon_h > icon_w:
        icon_h = icon_w
    # 把icon 调整为 调整是尺寸后的icon
    icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
    # 设置icon在img上的位置 为： img的中间位置
    w = int((img_w - icon_w) / 2)
    h = int((img_h - icon_h) / 2)
    # 把icon 黏贴到img上
    img.paste(icon, (w,h), icon)

    # 设置背景图
    bg = Image.open("/Users/lsy/PycharmProjects/wlb/goldbox-backend/static/pc/imgs/common/bg2.png")
    # 如果要求img_size 把背景调整为要求的大小
    if img_size:
        bg = bg.resize((img_size[0], img_size[1]), Image.ANTIALIAS)
    bg_w, bg_h = bg.size
    print bg.size
    # 根据背景图调整img的尺寸 如果img尺寸大于背景图高的1/2 调整尺寸为背景图的1/2
    size_w_1 = int(bg_w / 3)
    size_h_1 = int(bg_h / 2)
    # 如果img宽大于背景图，调整为背景图宽的1/3
    if img_w > size_w_1:
        img_w = size_w_1
    # 如果img高大于背景图，调整为背景图高的1/2
    if img_h > size_h_1:
        img_h = size_h_1
        img_w = size_h_1
    print img_w, img_h
    img = img.resize((img_w, img_h), Image.ANTIALIAS)
    img.show()
    # 把img粘贴在背景图 宽1/3 高1/2的位置
    w_1 = int((bg_w - img_w) / 3)
    h_1 = int((bg_h - img_h) / 2)
    bg.paste(img, (w_1, h_1), img)

    bg.show()
    # 为了使imagefield可以保存 生成的img文件对象，
    # 不需要把文件写入文件系统，通过StringIO和django InMemoryUploadedFile
    # 将文件重新插入内存， 返回文件文件类型
    # bg.save(path) 可以直接保存文件
    temp_handle = StringIO.StringIO()
    bg.save(temp_handle, format='JPEG')
    img_name = "%s.jpg" % createNoncestr()
    img_file = InMemoryUploadedFile(temp_handle, None, img_name, 'image/jpeg', temp_handle.len, None)
    return img_name, img_file

generate_qrcode_icon(code_url, (500, 200))