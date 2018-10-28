#!/usr/bin/python3
# encoding: utf-8
# @Time    :2018/9/18 16:16
# @Author  : xiaorui
# @File    : 1_login_by_code.py
# @Software: PyCharm
import math
import operator
import os
import random
import re
from functools import reduce
from io import BytesIO
from time import sleep

import requests
from PIL import Image
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 20)
browser.set_window_size(1440, 600)


def get_index():
    """获取技术漫画登录页面"""
    url = 'http://www.1kkk.com/'
    browser.get(url)

    login_click = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/header/div/div[2]/a/img')))
    login_click.click()

    return None


def get_position(num):
    """获取图片在页面中的位置"""
    # /html/body/section[3]/div/div/div/div/div/div[2]
    img = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/section[3]/div/div/div/div/div/div['+str(num+1)+']')))
    # time.sleep(2)
    print(f'====={num}=====')
    location = img.location
    size = img.size
    print(size)
    left, top, right, bottom = location['x'], location['y'], location['x'] + size['width'], location['y'] + size[
        'height']
    print(left, top, right, bottom)
    return left, top, right, bottom


def save_img():
    """通过网页截图保存需要验证的图片"""
    page_source = browser.page_source
    # 获取网页截图
    screenshot = browser.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    # screenshot.save('files/code_imgs/page.png')
    for i in range(1, 5):
        position = get_position(i)
        # 获取验证码图片
        captcha = screenshot.crop(position)
        img_url = 'files/code_imgs/img' + str(i) + '.png'
        captcha.save(img_url)
        print(f'the {i} save success')

def is_pixel_equal(image1, image2, x=10, y=60):
    """
    判断两个像素是否相同
    :param image1: 图片1
    :param image2: 图片2
    :param x: 位置x
    :param y: 位置y
    :return: 像素是否相同
    """
    # 取两个图片的像素点
    is_same = True
    for i in range(50):
        x = random.randint(5, 70)
        y = random.randint(5, 70)
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            pass
        else:
            is_same = False
    return is_same


def match_img(img1, img2):
    """匹配图片库中图片与目标图片,返回需要旋转次数"""
    for i in range(1, 5):
        j = 4 - i
        new_img2 = img2.rotate(j*90)
        if is_pixel_equal(img1, new_img2):
            print(f'{i}~~~~~~~~~~~~~~~~')
            return i
    return None


def filter_img(image1, image2):
    """ 初步筛选与验证图片相近的图片 """
    h1 = image1.histogram()
    h2 = image2.histogram()
    # print(image1, image2)
    result = math.sqrt(reduce(operator.add, list(map(lambda a, b: (a - b) ** 2, h1, h2))) / len(h1))
    if result < 20:
        return True
    return False


def rotation_num():
    """判断验证图片需要旋转的次数,返回点击次数的列表"""
    l_path = r'D:\04 spider\d05CheckCode\files\code_imgs'
    cimg_list = os.listdir(l_path)
    p_path = r'D:\04 spider\d05CheckCode\files\images_pool'
    img_pool = os.listdir(p_path)
    r_num = {}
    r_list = []
    print(cimg_list)
    for cimg_name in cimg_list:
        t = 1
        cimg = Image.open(l_path + '\\' + cimg_name)
        for img_name in img_pool:
            img = Image.open(p_path + '\\' + img_name)
            filter = filter_img(cimg, img)
            if filter:
                t += 1
                res = match_img(cimg, img)
                if res:
                    r_num[cimg_name] = 4 - res
                    print(img_name)
                    r_list.append(4-res)
        # print(t)
        print(r_list)
        # print(r_num, '==================')
    return r_list


def login(page_source, r_list):
    """输入用户信息,通过验证,实现登录"""
    page_source = browser.page_source
    # print(page_source)

    username = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/section[3]/div/div/div/div/p[2]/input')))
    password = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/section[3]/div/div/div/div/p[3]/input')))
    img1 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section[3]/div/div/div/div/div/div[2]')))
    img2 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section[3]/div/div/div/div/div/div[3]')))
    img3 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section[3]/div/div/div/div/div/div[4]')))
    img4 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section[3]/div/div/div/div/div/div[5]')))
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnLogin"]')))

    username.send_keys('wh')
    sleep(1)
    password.send_keys('123456')
    sleep(1)
    img_list = [img1, img2, img3, img4]
    i = 0
    while i < 4:
        for j in range(r_list[i]):
            img_list[i].click()
            sleep(0.5)
        i += 1
    login_button.click


def main():
    page_source = get_index()
    save_img()
    r_list = rotation_num()
    login(page_source, r_list)


if __name__ == '__main__':
    main()

