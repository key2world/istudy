# encoding:utf-8
import requests

# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=jrdi5DEUlpF4aLNNpCtaLsKg&client_secret=CBxyg0TruvBCuN58f0Lwm8b8YWfq0Q93'
response = requests.get(host)
if response:
    print(response.json())