# -*- coding: utf-8 -*-
import scrapy
import time
import json
from PIL import Image


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']

    # 重写start_requests方法，处理验证码问题
    def start_requests(self):
        t = str(time.time()).replace('','.')
        # 验证码url
        start_urls = "https://www.zhihu.com/captcha.gif?r={t}&type=login&lang=en".format(t=t)
        self.header ={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            'Referer':' https: // www.zhihu.com /'
        }
        # 请求验证码的url
        print(start_urls)
        return [scrapy.Request(url=start_urls,headers=self.header,callback=self.capcha,dont_filter=True)]

    # 获取验证码
    def capcha(self,response):
        # 获取验证码，将验证马写入本地
        with open('capcha.jpg','wb') as f:
            f.write(response.body)
        try:
            # 利用pillow打开验证码
            im = Image.open('capcha.jpg')
            im.show()
        except:
            print('请打开文件%s自行输入'%("capcha.jpg"))
        cap = input("请输入验证码>>")
        data = {
            "cap":cap
        }
        log_url = "https://www.zhihu.com/#signin"
        return scrapy.Request(url=log_url,callback=self.parse_login,headers=self.header,meta=data,dont_filter=True)

    def parse_login(self, response):
        xsrf = response.xpath('//input[@name="_xsrf"]/@value').extract_first()
        if not xsrf:
            print("找不到xsrf")
            return ''
        phone_num = input("请输入手机号码")
        password = input("请输入密码")
        data = {
            'captcha': response.meta['cap'],
            '_xsrf': xsrf,
            'password': password,
            'captcha_type': ' en',
            'phone_num': phone_num
        }
        # 用手机号-密码 登录的url
        url = 'https://www.zhihu.com/login/phone_num'
        return scrapy.FormRequest(url=url, callback=self.login_zh, headers=self.header, formdata=data, dont_filter=True,
                                  meta={'direct_list': [301, 302], 'direct_ignore': True})

    def login_zh(self, response):
        print(json.loads(response.text)['msg'])
        url = "https://www.zhihu.com/#signin"
        # 请求登录知乎
        yield scrapy.Request(url=url, callback=self.zh, headers=self.header, dont_filter=True,
                             meta={'direct_list': [301, 302], 'direct_ignore': True})

    # 后续解析知乎登录后的页面
    def zh(self, response):
        print(response.text)