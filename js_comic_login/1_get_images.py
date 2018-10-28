#!/usr/bin/python3
# encoding: utf-8
# @Time    :2018/9/17 22:04
# @Author  : xiaorui
# @File    : 1_get_images.py
# @Software: PyCharm
import re

import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
browser.set_window_size(1000, 500)


def get_index():
    """获取技术漫画登录页面"""
    url = 'http://www.1kkk.com/manhua41679/'
    browser.get(url)

    login_click = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/header/div/div[2]/a/img')))
    login_click.click()

    return None


def get_one_img(num):
    """下载验证码原图保存到本地"""
    page_source = browser.page_source
    # print(page_source)

    change_img_click = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'body > section > div > div > div > div > div > div:nth-child(1) > a')))
    wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/section/div/div/div/div/div/div[5]')))

    etree_html = etree.HTML(page_source)
    res = etree_html.xpath('/html/body/section/div/div/div/div/div/div[5]/@style')[0]
    print(res)
    img_url = 'http://www.1kkk.com/' + re.findall(r'url\("(.*?)"\)', res)[0]
    print(img_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre"
    }
    img = requests.get(img_url, headers=headers)
    print(img)
    with open('files/images/' + str(num) + '.png', 'wb') as f:
        f.write(img.content)

    change_img_click.click()


def main():
    """批量下载验证码原图"""
    page_source = get_index()
    for i in range(1000):
        get_one_img(i)


if __name__ == '__main__':
    main()


