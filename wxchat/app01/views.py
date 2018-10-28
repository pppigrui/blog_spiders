import json

from django.shortcuts import render, HttpResponse
import time
import requests
import re
from lxml import etree

# Create your views here.

# https://login.weixin.qq.com/qrcode/YeeDcdwvQA==

'''显示二维码'''

cookies = {}


def login(request):
    if request.method == 'GET':
        uuid_time = int(time.time() * 1000)
        base_uuid_url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={uuid_time}'
        uuid_url = base_uuid_url.format(uuid_time=uuid_time)
        r1 = requests.get(uuid_url)
        uuid = re.findall(r'window.QRLogin.uuid = "(.*?)";', r1.text, re.S)[0]

        # 放到session中后面可能会使用
        request.session['UUID_TIME'] = uuid_time
        request.session['UUID'] = uuid

        return render(request, 'login.html', {'uuid': uuid})


def get_ticket(html):
    '''
    获取凭证
    :param html:
    :return:
    '''
    etree_html = etree.HTML(html)
    ticket_dict = {}
    skey = etree_html.xpath('//skey/text()')[0]
    ret = etree_html.xpath('//ret/text()')[0]
    wxsid = etree_html.xpath('//wxsid/text()')[0]
    wxuin = etree_html.xpath('//wxuin/text()')[0]
    pass_ticket = etree_html.xpath('//pass_ticket/text()')[0]
    isgrayscale = etree_html.xpath('//isgrayscale/text()')[0]
    ticket_dict['skey'] = skey
    ticket_dict['ret'] = ret
    ticket_dict['wxsid'] = wxsid
    ticket_dict['wxuin'] = wxuin
    ticket_dict['pass_ticket'] = pass_ticket
    ticket_dict['isgrayscale'] = isgrayscale
    return ticket_dict


def check_login(request):
    # 扫码之后向微信发送的请求
    # https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=oda6i7RSng==&tip=0&r=-938029028&_=1538536286864
    response = {'code': 408, 'user_avatar': None}
    c_time = int(time.time() * 1000)
    base_login_url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={uuid}&tip=0&r=-938029028&_={time}'
    login_url = base_login_url.format(uuid=request.session['UUID'], time=c_time)
    # base_login_url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip=0&r=-735595472&_={1}"
    # login_url = base_login_url.format(request.session['UUID'], c_time)
    r1 = requests.get(login_url)

    # 无人扫码
    if 'window.code=408' in r1.text:
        response['code'] = 408

    # 扫码 返回头像界面
    elif 'window.code=201' in r1.text:
        response['code'] = 201
        # 获取头像的url
        user_avatar = re.findall(r"window.userAvatar = '(.*?)';", r1.text, re.S)[0]
        response['user_avatar'] = user_avatar
        print('扫码成功,请确认登录')

        '''扫码成功'''
    elif 'window.code=200' in r1.text:
        # https: // wx2.qq.com / cgi - bin / mmwebwx - bin / webwxnewloginpage?ticket = A1t1fjmCfIabsDVH33l7c5l0 @ qrticket_0 & uuid = 4cwyoHfZlQ == & lang = zh_CN & scan = 1538543558
        # https: // wx2.qq.com / cgi - bin / mmwebwx - bin / webwxnewloginpage?ticket = A6bE_JSYaipWad4K0evfUQSF @ qrticket_0 & uuid = QbxhjhZmmw == & lang = zh_CN & scan = 1538547684
        request.session['LOGIN_COOKIE'] = r1.cookies.get_dict()
        response['code'] = 200
        redirect_url = re.findall(r'redirect_uri="(.*?)";', r1.text, re.S)[0] + '&fun=new&version=v2&lang=zh_CN'
        # print(redirect_url)

        r2 = requests.get(redirect_url)
        # print(r2.text)#获取凭证（ticket）
        ticket = get_ticket(r2.text)
        # print(ticket)
        request.session['TICKET'] = ticket
        request.session['TICKET_COOKIE'] = r2.cookies.get_dict()

        init_url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-951782027&lang=zh_CN&pass_ticket={0}'.format(
            ticket.get('pass_ticket'))
        # 初始化联系人信息和公众号
        post_data = {
            "BaseRequest": {
                "DeviceID": "e534457976751681",
                "Sid": ticket['wxsid'],
                "Skey": ticket['skey'],
                "Uin": ticket['wxuin']
            }
        }
        # 以json传入的post请求 不是data是json
        r3 = requests.post(url=init_url, json=post_data)
        content = r3.content.decode('utf-8')
        init_dict = json.loads(content)
        # 用户初始化的信息
        request.session['INIT_DICT'] = init_dict
        # print(request.session['INIT_DICT'])
        # for k,v in init_dict.items():
        #     print(k,v)

        '''
        redirect_url中获取凭证 收发消息的时候要用ticket
        <error>
        <ret>0</ret>
        <message></message>
        <skey>@crypt_6ca2f576_b502613040001fcbc0ccf59165bd8782</skey>
        <wxsid>IQso/ovzSZK9SpEC</wxsid>
        <wxuin>518407033</wxuin>
        <pass_ticket>33sMB9RozwRSPGI3k3pOM0JV/24FpdeDQs7gL+t3QUe8EaGXpgYqaQJYxPx8GDhB</pass_ticket>
        <isgrayscale>1</isgrayscale>
        </error>
        '''
    return HttpResponse(json.dumps(response))


def avatar(request):
    # 显示最近联系人和公众号信息
    # /cgi-bin/mmwebwx-bin/webwxgeticon?seq=269790395&username=@f8c6c96914f69c69f708b08d15cfa56fe1f09a484a40a24a4a3e9f7ab644db91&skey=@crypt_6ca2f576_b8f0118ee30cb10c01cf6132884cab3b
    prev = request.GET.get('prev')  # /cgi-bin/mmwebwx-bin/webwxgeticon?seq=269790395
    username = request.GET.get('username')  # @f8c6c96914f69c69f708b08d15cfa56fe1f09a484a40a24a4a3e9f7ab644db91
    skey = request.GET.get('skey')  # @crypt_6ca2f576_b8f0118ee30cb10c01cf6132884cab3b
    img_url = 'https://wx2.qq.com{0}&username={1}&skey={2}'.format(prev, username, skey)
    cookies.update(request.session['TICKET_COOKIE'])
    cookies.update(request.session['LOGIN_COOKIE'])
    # print(img_url)
    res = requests.get(img_url, cookies=cookies, headers={'Content-Type': 'image/jpeg'})
    with open('a.jpg', 'wb') as f:
        f.write(res.content)
    return HttpResponse(res.content)


def index(request):
    return render(request, 'index.html')


def all_contact(request):
    # 获取所有联系人
    # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&r=1538638606854&seq=0&skey=@crypt_6ca2f576_f274d2aa48510a24bcd14003a0757eff
    ctime = int(time.time() * 1000)
    base_url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&r={0}&seq=0&skey={1}'
    url = base_url.format(ctime, request.session['TICKET']['skey'], headers={'Connection': 'keep-alive',
                                                                             'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'})
    res = requests.get(url, cookies=cookies)
    res.encoding = 'utf-8'
    contact_list = json.loads(res.text)['MemberList']
    # print(res.text)
    # print(contact_list)
    return render(request, 'all_contact.html', {'contact_list': contact_list})  # {'contact_list':contact_list}


def send_msg(request):
    if request.method == 'POST':
        ticket = request.session['TICKET']
        send_user = request.session['INIT_DICT']['User']['UserName']
        to = request.POST.get('to')
        msg = request.POST.get('msg')

        url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket={0}'.format(
            ticket['pass_ticket'])
        ctime = int(time.time() * 1000)
        post_data = {
            "BaseRequest": {
                "DeviceID": "e534457976751681",
                "Sid": ticket['wxsid'],
                "Skey": ticket['skey'],
                "Uin": ticket['wxuin']
            },
            "Msg": {
                'ClientMsgId': ctime,
                'Content': msg,
                'FromUserName': send_user,
                'LocalID': ctime,
                'ToUserName': to,
                'Type': 1
            },
            "Scene": 0
        }

        res = requests.post(url=url, data=json.dumps(post_data, ensure_ascii=False).encode('utf-8'),
                            headers={'Content-Type': 'application/json'})
        # print(res)
        return HttpResponse('发送消息成功')


# def get_msg(request):
#     """
#     长轮询获取消息
#     :param request:
#     :return:
#     """
#     # 检查是否有消息到来
#     ctime = int(time.time() * 1000)
#     ticket_dict = request.session['TICKET']
#     check_msg_url = "https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck"
#
#     synckey_dict = request.session['INIT_DICT']['SyncKey']
#     synckey_list = []
#     for item in synckey_dict['List']:
#         tmp = "%s_%s" % (item['Key'], item['Val'])
#         synckey_list.append(tmp)
#     synckey = "|".join(synckey_list)
#
#     r1 = requests.get(
#         url=check_msg_url,
#         params={
#             'r': ctime,
#             "deviceid": "e384757757885382",
#             'sid': ticket_dict['wxsid'],
#             'uin': ticket_dict['wxuin'],
#             'skey': ticket_dict['skey'],
#             '_': ctime,
#             'synckey': synckey
#         },
#         cookies=cookies
#     )
#     # print(r1.text)
#     if '{retcode:"0",selector:"0"}' in r1.text:
#         return HttpResponse('...')
#
#     # 有消息，获取消息
#     base_get_msg_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid={0}&skey={1}&lang=zh_CN&pass_ticket={2}"
#     get_msg_url = base_get_msg_url.format(ticket_dict['wxsid'], ticket_dict['skey'], ticket_dict['pass_ticket'])
#
#     post_data = {
#         "BaseRequest": {
#             "DeviceID": "e384757757885382",
#             'Sid': ticket_dict['wxsid'],
#             'Uin': ticket_dict['wxuin'],
#             'Skey': ticket_dict['skey'],
#         },
#         'SyncKey': request.session['INIT_DICT']['SyncKey']
#     }
#     r2 = requests.post(
#         url=get_msg_url,
#         json=post_data,
#         cookies=cookies
#     )
#     r2.encoding = 'utf-8'
#     # 接受到消息： 消息，synckey
#     msg_dict = json.loads(r2.text)
#     # print(msg_dict)
#     for msg in msg_dict['AddMsgList']:
#         print('您有新消息到来：', msg['Content'])
#     init_dict = request.session['INIT_DICT']
#     init_dict['SyncKey'] = msg_dict['SyncKey']
#     request.session['INIT_DICT'] = init_dict
#
#     return HttpResponse('...')


def get_msg(request):
    """
    长轮询获取消息
    :param req:
    :return:
    """
    # 检查是否有消息到来
    ctime = int(time.time() * 1000)
    ticket_dict = request.session['TICKET']
    check_msg_url = "https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck"

    synckey_dict = request.session['INIT_DICT']['SyncKey']
    synckey_list = []
    for item in synckey_dict['List']:
        tmp = "%s_%s" % (item['Key'], item['Val'])
        synckey_list.append(tmp)
    synckey = "|".join(synckey_list)

    r1 = requests.get(
        url=check_msg_url,
        params={
            'r': ctime,
            "deviceid": "e384757757885382",
            'sid': ticket_dict['wxsid'],
            'uin': ticket_dict['wxuin'],
            'skey': ticket_dict['skey'],
            '_': ctime,
            'synckey': synckey
        },
        cookies=cookies
    )
    print(r1.text)
    if '{retcode:"0",selector:"0"}' in r1.text:
        return HttpResponse('...')

    # 有消息，获取消息
    base_get_msg_url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid={0}&skey={1}&lang=zh_CN&pass_ticket={2}"
    get_msg_url = base_get_msg_url.format(ticket_dict['wxsid'], ticket_dict['skey'], ticket_dict['pass_ticket'])

    post_data = {
        "BaseRequest": {
            "DeviceID": "e384757757885382",
            'Sid': ticket_dict['wxsid'],
            'Uin': ticket_dict['wxuin'],
            'Skey': ticket_dict['skey'],
        },
        'SyncKey': request.session['INIT_DICT']['SyncKey']
    }
    r2 = requests.post(
        url=get_msg_url,
        json=post_data,
        cookies=cookies
    )
    r2.encoding = 'utf-8'
    # 接受到消息： 消息，synckey
    msg_dict = json.loads(r2.text)
    print(msg_dict)
    for msg in msg_dict['AddMsgList']:
        print('您有新消息到来：', msg['Content'])
    init_dict = request.session['INIT_DICT']
    init_dict['SyncKey'] = msg_dict['SyncKey']
    request.session['INIT_DICT'] = init_dict

    return HttpResponse('...')
