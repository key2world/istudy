from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, reverse
import re
from istudy import settings  # 自己导入文件，其中配置大写小写没有用
from app01 import models


# from django.conf import global_settings, settings

# global_settings默认配置
# settings 不是settings的文件 点进去生成的是一个类似settings的对象
# 这个对象里边包含了默认配置，以及自己写的settings文件的配置
# 这个settings要导入settings文件中写的配置必须是大写的，小写没有用
class AuthMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        # 需要登录后才能访问的地址 需要判断登录状态
        # 默认所有的地址都是需要登录才能访问的
        # 设置一个白名单 不登录就能访问
        url = request.path_info

        # print(url)

        # 先验证登录在验证白名单
        # 校验登录状态
        is_login = request.session.get("is_login")
        if is_login:
            # 已经登录了  可以访问
            obj = models.User.objects.filter(pk=request.session.get("pk")).first()
            request.user_obj = obj  # 用户对象 # 给request赋值属性  后边用到在取
            # （但是不能使用request.user应为有这个属性，如果赋值会把系统的这个属性覆盖掉）
            return

        # 白名单
        for i in settings.WHITE_LIST:
            # re.search是搜索字符串的第一个位置  返回match对象 使用match.group(0)
            # re.match是从一个字符串的开始位置起匹配正则表达式  返回match对象 使用match.group(0)（**如果不是这个开头就没有返回值）
            # re.findall 搜索字符串 以列表类型返回全部匹配到的子串
            if re.match(i, url):
                # 因为上边的地址改为了正则表达式，所以下边要用match来匹配，匹配到是一个对象
                return
        if url == "/check_user_name/":  # 使用ajax验证用户名是否重复  不然会有重定向错误 就是应为没有登录所以会先给url地址加url="",就会产生错误
            # 这个错误还可以再白名单解决
            return
        if url == "/check_password/":
            return
        if url == "/check_re_pwd/":
            return

            # 没有登录 需要去登录  登录之后在去跳转到之前的那个页面
        return redirect("{}?url={}".format(reverse("login"), url))
