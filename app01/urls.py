from django.conf.urls import url
from app01 import views

urlpatterns = [
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^register/$', views.register, name="register"),
    url(r'^index/$', views.index, name="index"),
    url(r'^article/(\d+)/$', views.article, name="article"),

    # 检查用户名是否重复
    url(r'^check_user_name/', views.check_user_name, name="check_user_name"),
    # 检查密码是否设置正确
    url(r'^check_password/', views.check_password, name="check_password"),
    # 检查两次密码输入是否一致
    url(r'^check_re_pwd/', views.check_re_pwd, name="check_re_pwd"),
    # 检查验证码是否正确
    url(r'^check_captcha/', views.check_captcha, name="check_captcha"),

    # 用户错输地址
    url(r'^article/$', views.index),

    # 后台
    url(r'^backend/$', views.backend, name="backend"),

    # 文章
    url(r'^article_list/$', views.article_list, name="article_list"),
    url(r'^article_add/$', views.article_add, name="article_add"),
    url(r'^article_edit/(\d+)/$', views.article_edit, name="article_edit"),
    url(r'^article_delete/(\d+)/$', views.article_delete, name="article_delete"),

    # 分页
    url(r'^user_list/$', views.user_list, name="user_list"),

    # 分类
    url(r'^category_list/$', views.category_list, name="category_list"),
    url(r'^category_add/$', views.category_add, name="category_add"),
    url(r'^category_edit/(\d+)/$', views.category_edit, name="category_edit"),
    url(r'^category_del/(\d+)/$', views.category_del, name="category_del"),

    # 评论
    url(r'^comment/$', views.comment, name="comment"),
    url(r'^comment_del/(\d+)/$', views.comment_del, name="comment_del"),

    # 系列
    url(r'^series_list/$', views.series_list, name="series_list"),
    url(r'^series_add/$', views.series_change, name="series_add"),  # 和下边路由使用同一个函数实现功能
    url(r'^series_edit/(\d+)/$', views.series_change, name="series_edit"),  # 对于是对一张表的增和改可以这样操作
    url(r'^series_del/(\d+)/$', views.series_del, name="series_del"),

    # 系列完成度展示
    url(r"^profile/$", views.profile, name="profile"),

    # 校验（注册用户名ajax校验）
    url(r"^check/$", views.check, name="check"),

    # 积分
    url(r"^point/$", views.point, name="point"),

    # 测试
    url(r"^ceshi/$", views.ceshi, name="ceshi"),

    # 给别人展示的个人页面
    url(r"^user_profile/(\d+)/$", views.user_profile, name="user_profile"),

    # 容错 内网穿透
    url(r'^$', views.index, name="index"),  # 首页

]
