# encoding:utf-8

import requests
import base64
import json

'''
通用物体和场景识别
'''


def ww(x):
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
    # 二进制方式打开图片文件
    f = open(x, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}
    access_token = '24.24faf03186dad17c7154ad00d17cb4ea.2592000.1610545134.282335-23152206'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        # print(response.json())
        value = "置信度:", json.loads(response.text).get("result")[0].get('score'), "属性:", \
                json.loads(response.text).get("result")[0].get('root'),  "名称:", \
                json.loads(response.text).get("result")[0].get('keyword')
        print(value)
        return value
