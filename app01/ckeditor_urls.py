from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required  # 装饰器 校验
from django.views.decorators.cache import never_cache

from ckeditor_uploader import views

urlpatterns = [
    url(r"^upload/", views.upload, name="ckeditor_upload"),
    url(
        r"^browse/",
        never_cache(views.browse),
        name="ckeditor_browse",
    ),
]
