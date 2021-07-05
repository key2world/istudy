from django import template
from django.shortcuts import reverse
from django.http.request import QueryDict
from django.utils import timezone  # 将utc时间转换为当前时区的时间

register = template.Library()


# 为了将url地址中的参数 替换为urlencode
@register.simple_tag
def reverse_url(request, name, *args, **kwargs):
    qd = QueryDict(mutable=True)
    url = request.get_full_path()  # 没有经过urlencode编码，所以会出现问题  就是&分隔符的问题  可以使用QueryDict进行编码
    qd["url"] = url
    return "{}?{}".format(reverse(name, args=args, kwargs=kwargs), qd.urlencode())


# 为了将后台获取到的UTC时间修改为中国时间
@register.simple_tag
def modify_times(time, *args, **kwargs):
    return timezone.localtime(time).strftime("%Y-%m-%d %H:%M:%S")
