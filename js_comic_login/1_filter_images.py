#!/usr/bin/python3
# encoding: utf-8
# @Time    :2018/9/18 10:33
# @Author  : xiaorui
# @File    : 1_filter_images.py
# @Software: PyCharm
import os
import re
from PIL import Image
#使用第三方库：Pillow
import math
import operator
from functools import reduce
from pixel_match_img import match

"""可用VisiPics软件精确去重"""



def del_extra_imgs():
    path = (r'D:\04 spider\d05CheckCode\files\split_images')
    filelist = os.listdir(path)  # 该文件夹下所有的文件（包括文件夹）
    print(len(filelist))
    for files in filelist:  # 遍历所有文件
        # Olddir = os.path.join(path, files);  # 原来的文件路径
        filename = os.path.splitext(files)[0]  # 文件名
        exp = re.compile(r'\d*?_[0-3]$')
        if exp.match(filename):  # 如果是前四张图则略过
            print(f'filter{files}')
            continue
        os.remove(os.path.join(path, files))
        print(f'{files} has been deleted')


def rename_imgs():
    """批量重命名文件"""
    i = 0
    new_path = (r'D:\04 spider\d05CheckCode\files\split_images')
    path = (r'D:\04 spider\d05CheckCode\files\images_pool')
    filelist = os.listdir(path)  # 该文件夹下所有的文件（包括文件夹）
    print(len(filelist))
    for files in filelist:  # 遍历所有文件
        i = i + 1
        Olddir = os.path.join(path, files);  # 原来的文件路径
        filename = os.path.splitext(files)[0]  # 文件名

        new_filename = str(i)
        filetype = os.path.splitext(files)[1]
        print(filename + filetype)
        Newdir = os.path.join(new_path, new_filename + filetype)  # 新的文件路径
        os.rename(Olddir, Newdir)  # 重命名


def del_repeated_imgs():
    """删除重复文件"""
    path = (r'D:\04 spider\d05CheckCode\files\images_pool')
    filelist = os.listdir(path)  # 该文件夹下所有的文件（包括文件夹）
    img_num = len(filelist) + 1
    print(img_num)
    for i in range(1, img_num):
        try:
            img_name = str(i) + '.png'
            image1=Image.open(path + '\\' + img_name)
            print(f'start comparison {img_name}')
        except FileNotFoundError as e:
            # print(e)
            continue
        for j in range((i+1), img_num):
            try:
                image2=Image.open(path + '\\' + str(j) + '.png')
            except FileNotFoundError as e:
                # print(e)
                continue
            #把图像对象转换为直方图数据，存在list h1、h2 中
            # h1=image1.histogram()
            # h2=image2.histogram()
            # # print(image1, image2)
            # result = math.sqrt(reduce(operator.add,  list(map(lambda a,b: (a-b)**2, h1, h2)))/len(h1) )
            '''
            sqrt:计算平方根，reduce函数：前一次调用的结果和sequence的下一个元素传递给operator.add
            operator.add(x,y)对应表达式：x+y
            这个函数是方差的数学公式：S^2= ∑(X-Y) ^2 / (n-1)
            '''
            # print(result)
            #result的值越大，说明两者的差别越大；如果result=0,则说明两张图一模一样

            result = match(image1, image2)
            if result < 10:
            # if result:
                img_name = str(j) + '.png'
                os.remove(os.path.join(path, img_name))
                print(f'{img_name}has been deleted')

def test():
    path = (r'D:\04 spider\d05CheckCode\files\images_pool')
    filelist = os.listdir(path)  # 该文件夹下所有的文件（包括文件夹）
    img_num = len(filelist) + 1
    # print(img_num)
    image1 = Image.open(path + '\\' + str(39) + '.png')

    image2 = Image.open(path + '\\' + str(56) + '.png')

    # 把图像对象转换为直方图数据，存在list h1、h2 中
    h1 = image1.histogram()
    h2 = image2.histogram()
    # print(image1, image2)
    result = math.sqrt(reduce(operator.add, list(map(lambda a, b: (a - b) ** 2, h1, h2))) / len(h1))
    '''
    sqrt:计算平方根，reduce函数：前一次调用的结果和sequence的下一个元素传递给operator.add
    operator.add(x,y)对应表达式：x+y
    这个函数是方差的数学公式：S^2= ∑(X-Y) ^2 / (n-1)
    '''
    print(result)
    # result的值越大，说明两者的差别越大；如果result=0,则说明两张图一模一样
    # if result < 10:
    #     img_name = str(72) + '.png'
    #     os.remove(os.path.join(path, img_name))
    #     print(f'{img_name} has been deleted')


def main():
    # del_extra_imgs()
    rename_imgs()
    # del_repeated_imgs()
    # test()


if __name__ == '__main__':
    main()
