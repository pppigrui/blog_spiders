# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, Spider
import json
import hmac
import json
import time
import base64
from hashlib import sha1
from scrapy.http.cookies import CookieJar

from zhihuuser.items import ZhihuuserItem


class ZhihuSpider(scrapy.Spider):
    num = 0
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    # agent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'
    headers = {
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': agent,
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
    }
    grant_type = 'password'
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    source = 'com.zhihu.web'
    timestamp = str(int(time.time() * 1000))
    timestamp2 = str(time.time() * 1000)
    print(timestamp2)

    start_user = 'Germey'

    # user_url =
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_include = 'allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    def get_signature(self, grant_type, client_id, source, timestamp):
        """处理签名"""
        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        hm.update(str.encode(grant_type))
        hm.update(str.encode(client_id))
        hm.update(str.encode(source))
        hm.update(str.encode(timestamp))
        return str(hm.hexdigest())

    def parse(self, response):
        print(response.body.decode("utf-8"))

    def start_requests(self):
        yield scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                             headers=self.headers, callback=self.is_need_capture)

    def is_need_capture(self, response):
        print(response.text)
        need_cap = json.loads(response.body)['show_captcha']
        print(need_cap)

        if need_cap:
            print('需要验证码')
            yield scrapy.Request(
                url='https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                headers=self.headers,
                callback=self.capture,
                method='PUT'
            )
        else:
            print('不需要验证码')
            post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
            post_data = {
                "client_id": self.client_id,
                "username": "18109086348",  # 输入知乎用户名
                "password": "xr123456789",  # 输入知乎密码
                "grant_type": self.grant_type,
                "source": self.source,
                "timestamp": self.timestamp,
                "signature": self.get_signature(self.grant_type, self.client_id, self.source, self.timestamp),  # 获取签名
                "lang": "en",
                "ref_source": "homepage",
                "captcha": '',
                "utm_source": "baidu"
            }
            yield scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.headers,
                callback=self.check_login
            )
        # yield scrapy.Request('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
        #                      headers=self.headers, callback=self.capture, meta={"resp": response})
        # yield scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
        #                      headers=self.headers, callback=self.capture, meta={"resp": response},dont_filter=True)

    def capture(self, response):
        # print(response.body)
        try:
            img = json.loads(response.body)['img_base64']
        except ValueError:
            print('获取img_base64的值失败！')
        else:
            img = img.encode('utf8')
            img_data = base64.b64decode(img)

            with open('zhihu03.gif', 'wb') as f:
                f.write(img_data)
                f.close()
        captcha = input('请输入验证码：')
        post_data = {
            'input_text': captcha
        }
        yield scrapy.FormRequest(
            url='https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
            formdata=post_data,
            callback=self.captcha_login,
            headers=self.headers
        )

    def captcha_login(self, response):
        try:
            cap_result = json.loads(response.body)['success']
            print(cap_result)
        except ValueError:
            print('关于验证码的POST请求响应失败!')
        else:
            if cap_result:
                print('验证成功!')
        post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        post_data = {
            "client_id": self.client_id,
            "username": "18109086348",  # 输入知乎用户名
            "password": "xr123456789",  # 输入知乎密码
            "grant_type": self.grant_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "signature": self.get_signature(self.grant_type, self.client_id, self.source, self.timestamp),  # 获取签名
            "lang": "en",
            "ref_source": "homepage",
            "captcha": '',
            "utm_source": ""
        }
        headers = self.headers
        headers.update({
            'Origin': 'https://www.zhihu.com',
            'Pragma': 'no - cache',
            'Cache-Control': 'no - cache'
        })
        yield scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=headers,
            callback=self.check_login,
            meta={'cookiejar': True}
        )

    def check_login(self, response):
        # 验证是否登录成功
        text_json = json.loads(response.text)
        # print(text_json)
        print('登录成功')

        yield scrapy.Request('https://www.zhihu.com/', headers=self.headers, callback=self.start_user,
                             meta={'cookiejar': True})

    def start_user(self, response):

        yield Request(
            url='https://www.zhihu.com/api/v4/members/Germey/followees?include=data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics&offset=0&limit=20'
            , callback=self.get_follws, meta={'cookiejar': True})

    def get_follws(self, response):
        result_dict = json.loads(response.text)
        # print(type(result_dict))
        for i in range(20):
            self.num += 1
            url_token = result_dict['data'][i]['url_token']
            name = result_dict['data'][i]['name']
            print('第%s条信息,用户名：%s' % (self.num, name))
            #         # print(url_token)
            yield Request(url=self.user_url.format(user=url_token, include=self.user_include),
                          callback=self.get_user_info)

        if result_dict['paging'] and result_dict['paging']['is_end'] == False:
            yield Request(url=result_dict['paging']['next'], callback=self.get_follws, meta={'cookiejar': True})

            print('-------')
        yield Request(url=self.follows_url.format(user=url_token, include=self.follows_include, offset=0, limit=20),
                      callback=self.get_follws)

        yield Request(url=self.follows_url.format(user=url_token, include=self.follows_include, offset=0, limit=20),
                      callback=self.get_follwers)

    def get_follwers(self, response):
        result_dict = json.loads(response.text)
        # print(type(result_dict))
        for i in range(20):
            url_token = result_dict['data'][i]['url_token']
            name = result_dict['data'][i]['name']
            print(name)
            #         # print(url_token)
            yield Request(url=self.user_url.format(user=url_token, include=self.user_include),
                          callback=self.get_user_info)

        if result_dict['paging'] and result_dict['paging']['is_end'] == False:
            yield Request(url=result_dict['paging']['next'], callback=self.get_follwers, meta={'cookiejar': True})
        yield Request(url=self.follows_url.format(user=url_token, include=self.get_follwers, offset=0, limit=20),
                      callback=self.get_follwers)

    def get_user_info(self, response):
        result = json.loads(response.text)
        item = ZhihuuserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)

        yield item
