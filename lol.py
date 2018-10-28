#!/usr/bin/python3
# encoding: utf-8
# @Time    :17-08-20 下午3:44
# @Author  : xiaorui
# @File    : lol.py
# @Software: PyCharm

import requests
import re
import json


def get_hero_info(url_js):
    """
    获取到英雄的信息
    :param url_js: 存放信息的jsurl
    :return: 英雄信息
    """
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
    }
    res = requests.get(url_js, headers=headers)
    hero_info = re.findall(r'champion={"keys":(.*?),"data":{"Aatrox"', res.text)[0]
    dict_hero_info = json.loads(hero_info)
    return dict_hero_info


def get_hero_img_url(dict_hero_info):
    """
    获取英雄的皮肤
    :param dict_hero_info: 英雄信息
    :return: 原始皮肤图片的地址
    """
    hero_img_url = []
    for hero_num in dict_hero_info.keys():
        hero_name = dict_hero_info[hero_num]
        hero_img_url.append('ossweb-img.qq.com/images/lol/img/champion/%s.png' % hero_name)
    return hero_img_url


def get_hero_skin_url(dict_hero_info):
    """获取英雄所有皮肤的url"""
    hero_skin_img_url = []
    for hero_num in dict_hero_info.keys():
        num = 0
        for i in range(20):
            num += 1
            if len(str(num)) == 1:
                num = '00' + str(num)
            elif len(str(num)) == 2:
                num = '0' + str(num)
            hero_skin_img_url.append('http://ossweb-img.qq.com/images/lol/web201310/skin/big%s%s.jpg' % (hero_num, num))
            num = int(num)

    return hero_skin_img_url

def main():
    # 将图片存入本地文件夹
    url_js = 'http://lol.qq.com/biz/hero/champion.js'
    dict_hero_info = get_hero_info(url_js)
    hero_skin_img_urls = get_hero_skin_url(dict_hero_info)

    num = 0
    for hero_skin_img_url in hero_skin_img_urls:
        num += 1
        hero_name = re.findall(r'/skin/big(.*?).jpg', hero_skin_img_url)
        r = requests.get(hero_skin_img_url)
        if r.status_code == 200:
            with open('./images/%s.png' % hero_name[0], 'wb')as f:
                # 要想得到图片必须写入图片的二进制码，也就是response.content
                f.write(r.content)
                print('第%s张图片下载成功' % num)
        else:
            print('第%s张图片不存在' % num)


if __name__ == '__main__':

    main()