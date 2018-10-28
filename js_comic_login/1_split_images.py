#!/usr/bin/python3
# encoding: utf-8
# @Time    :2018/9/18 8:43
# @Author  : xiaorui
# @File    : 1_split_images.py
# @Software: PyCharm

import os
from PIL import Image

def splitimage(src, rownum, colnum, dstpath, i):
    """将验证码原图分割成小图"""
    img = Image.open(src)
    w, h = img.size
    if rownum <= h and colnum <= w:
        print('Original image info: %sx%s, %s, %s' % (w, h, img.format, img.mode))
        print(f'开始处理第{i}张图片切割, 请稍候...')

        s = os.path.split(src)
        if dstpath == '':
            dstpath = s[0]
        fn = s[1].split('.')
        basename = fn[0]
        ext = fn[-1]

        num = 0
        rowheight = h // rownum
        colwidth = w // colnum
        # for r in range(rownum):
        r = 0
        for c in range(colnum):
            # 获取第一行的四张小图
            box = (c * colwidth, r * rowheight, (c + 1) * colwidth, (r + 1) * rowheight)
            img.crop(box).save(os.path.join(dstpath, basename + '_' + str(num) + '.' + ext), ext)
            num = num + 1

        print('图片切割完毕，共生成 %s 张小图片。' % num)
    else:
        print('不合法的行列切割参数！')


def main():
    """批量切割验证码图片"""
    # 图片输入路径
    for i in range(1):
        src = 'files/images/' + str(i) + '.png'
        if os.path.isfile(src):
            # 图片输出路径
            dstpath = 'files/split_images/'
            if (dstpath == '') or os.path.exists(dstpath):
                # 切割行数和列数
                row = 4
                col = 4
                if row > 0 and col > 0:
                    splitimage(src, row, col, dstpath, i)
                else:
                    print('无效的行列切割参数！')
            else:
                print('图片输出目录 %s 不存在！' % dstpath)
        else:
            print('图片文件 %s 不存在！' % src)


if __name__ == '__main__':
    main()