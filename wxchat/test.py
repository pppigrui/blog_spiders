#!/usr/bin/python3
# encoding: utf-8
# @Time    :18-10-4 下午4:52
# @Author  : xiaorui
# @File    : test.py
# @Software: PyCharm

# import json
#
# # json.dumps()函数的使用，将字典转化为字符串
# dict1 = {"age": "12"}
# json_info = json.dumps(dict1)
# print(json_info)
# print("dict1的类型："+str(type(dict1)))
# print("通过json.dumps()函数处理：")
# print("json_info的类型："+str(type(json_info)))

import json

# json.loads函数的使用，将字符串转化为字典
json_info = '{"age": "12"}'
dict1 = json.loads(json_info)
print("json_info的类型："+str(type(json_info)))
print("通过json.dumps()函数处理：")
print("dict1的类型："+str(type(dict1)))