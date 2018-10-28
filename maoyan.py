#!/usr/bin/python3
# encoding: utf-8
# @Time    :17-7-28 下午2:14
# @Author  : xiaorui
# @File    : maoyan.py
# @Software: PyCharm


import json
import requests
from requests.exceptions import RequestException
import re
import time


def get_one_page(url):
    """
    获取一页的网页源代码
    :param url: 抓取的第一页的网页地址
    :return: 网页源代码
    """
    try:
        # 添加请求头，模仿浏览器防止反爬
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    """
    解析网页源代码获取电影信息
    :param html: 网页源代码
    :return: 电影信息
    """
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }


def write_to_file(content):
    """
    写入文件
    :param content: 电影信息
    :return:
    """
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(offset):
    """
    抓取所有要抓的信息
    :param offset:
    :return:
    """
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    for i in range(10):
        main(offset=i * 10)
        time.sleep(1)

