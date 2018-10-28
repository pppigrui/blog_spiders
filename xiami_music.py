#!/usr/bin/python3
# encoding: utf-8
# @Time    :17-09-20 下午5:14
# @Author  : xiaorui
# @File    : xiami_music.py
# @Software: PyCharm

import os
import time
from urllib.parse import quote

import requests
from selenium import webdriver

from selenium.webdriver.common.by import By


from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pymongo

import urllib
from urllib import parse

broswer = webdriver.Chrome()


def get_mp3_data():
    """获取虾米音乐MP3的歌名和得到url所需要的密码字段"""
    try:
        url = 'https://www.xiami.com/chart?spm=a1z1s.6843761.1110925385.2.tz9DXJ'
        broswer.get(url)

        wait = WebDriverWait(broswer, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.songwrapper')))
        page_source = broswer.page_source

        html = etree.HTML(page_source)
        # print(html)
        mp3_infos = html.xpath('//div[@id="chart"]/table/tr')
        # print(mp3_infos)
        for mp3_info in mp3_infos:
            info = {}
            info['title'] = mp3_info.xpath('./@data-title')[0]
            info['url'] = mp3_info.xpath('.//@data-mp3')[0]
            yield info
    except:
        get_mp3_data()


def parse_mp3_data(mp3_data):
    """凯撒密码解法破解密码得到真正的url"""
    num_loc = mp3_data.find('h')
    rows = int(mp3_data[0:num_loc])
    strlen = len(mp3_data) - num_loc
    cols = int(strlen / rows)
    right_rows = strlen % rows
    new_s = list(mp3_data[num_loc:])
    output = ''
    for i in range(len(new_s)):
        x = i % rows
        y = i / rows
        p = 0
        if x <= right_rows:
            p = x * (cols + 1) + y
        else:
            p = right_rows * (cols + 1) + (x - right_rows) * cols + y
        output += new_s[int(p)]
    return parse.unquote(output).replace('^', '0')


def save_to_mongo(info):
    """存储到mongodb"""
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.xiami_music
    collection = db.musics
    collection.insert(info)
    # print("存储到mongo成功")


def download_music(mp3_url, title):
    """下载音乐"""
    res = requests.get(mp3_url)
    if not os.path.exists('musci'):
        os.mkdir('music')
    with open('./music/%s.mp3' % title, 'wb')as f:
        f.write(res.content)


def main():
    num = 0
    for info in get_mp3_data():
        num += 1
        mp3_data = info['url']
        mp3_url = parse_mp3_data(mp3_data)
        title = info['title']
        download_music(mp3_url, title)
        print('第%s首歌下载成功' % num)
        # print(mp3_url)
        # print(info)


if __name__ == '__main__':
    main()
