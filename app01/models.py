from django.db import models
from django.utils.safestring import mark_safe
import datetime


# Create your models here.
class User(models.Model):
    """
    员工信息表
        用户名 密码 职位 公司名（子，总公司）手机号 最后一次登录时间
    """
    username = models.CharField(max_length=32, verbose_name="用户名", unique=True)
    password = models.CharField(max_length=32, verbose_name="密码")
    position = models.CharField(max_length=32, verbose_name="职位")  # 职位
    company = models.CharField(max_length=32, verbose_name="公司",
                               choices=(("0", "北京总公司"), ("1", "石家庄分公司"), ("2", "广州分公司")))  # 公司名
    phone = models.CharField(max_length=11, verbose_name="手机号")
    last_time = models.DateTimeField(null=True, blank=True, verbose_name="最后一次登录时间")  # 数据库中可以为空，用户输入也可以为空
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="用户创建时间")  # 用户创建时间 auto_now_add新增数据时自动保存时间
    is_active = models.BooleanField(default=True)  # 是否可以登录

    avatar = models.ImageField(upload_to="img/avatar", default="img/avatar/back.jpg", verbose_name="用户头像")

    def __str__(self):
        return self.username


class Category(models.Model):  # Category分类   板块
    title = models.CharField(max_length=64, verbose_name="板块标题")

    def __str__(self):
        return self.title


class Article(models.Model):
    """
     文章表
        标题 文章摘要 作者 板块 创建时间 更新时间 删除状态
    """
    title = models.CharField(max_length=64, verbose_name="文章标题")
    abstract = models.CharField(max_length=256, verbose_name="文章摘要")
    author = models.ForeignKey("User", on_delete=models.DO_NOTHING, null=True,
                               verbose_name="作者")  # 外键  写到多的一方 作者删除之后什么都不做
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING, null=True,
                                 blank=True, verbose_name="板块")  # 外键  写到多的一方 一个板块多个文章
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    publish_status = models.BooleanField(default=False, choices=((False, "未发布"), (True, "发布")), verbose_name="发布状态")

    point = models.IntegerField(default=0, verbose_name="积分")
    duration = models.DurationField(default=datetime.timedelta(), verbose_name="推荐阅读时间")  # 时间间隔  timedelta()相当于0

    detail = models.OneToOneField("ArticleDetail", on_delete=models.DO_NOTHING)

    # 一对一 和foreignkey一样但是有一个unique的约束，就是唯一的
    def __str__(self):
        return self.title

    def show_publisher(self):
        color_dict = {False: "red", True: "green"}
        return mark_safe(
            '<span style="background: {};color: white;padding: 3px">{}</span>'.format(color_dict[self.publish_status],
                                                                                      self.get_publish_status_display()))


from ckeditor_uploader.fields import RichTextUploadingField  # 富文本编辑器，为了修改数据库中的字段


class ArticleDetail(models.Model):
    """
    文章详情表
        一一对应
    """
    # content = models.TextField(verbose_name="文章内容")  # 普通文本框
    content = RichTextUploadingField(verbose_name="文章内容")  # 富文本编辑框


class Comment(models.Model):
    """
    评论表
        评论者 评论内容 评论文章 时间 审核状态
    """
    author = models.ForeignKey("User", verbose_name="评论者", on_delete=models.DO_NOTHING)
    content = models.TextField(verbose_name="内容")
    article = models.ForeignKey("Article", verbose_name="文章", on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    status = models.BooleanField(verbose_name="审核状态", default=True)

    # parent = models.ForeignKey("self", null=True, blank=True)  # parent_id 二级评论时填写


class Series(models.Model):
    """
    series系列
    系列和文章  是多对多关系
    系列和用户  是多对多关系
    """
    title = models.CharField(max_length=32, verbose_name="系列的名称")
    articles = models.ManyToManyField("Article", verbose_name="文章")
    users = models.ManyToManyField("User", verbose_name="用户", through="UserSeries")
    # 创建第三张表 through="UserSeries"使用这个参数就不会创建第三张表  但是关系方法还是可以使用的


class UserSeries(models.Model):
    """
    Series_users  多对多自己创建的表   但是自己也可以创建
    id series_id users_id   progress进度  想自己创建的字段
    1     1        1            66.66
    2     2        1            0
    3     1        2            0
    """
    user = models.ForeignKey("User", verbose_name="用户", on_delete=models.DO_NOTHING)
    series = models.ForeignKey("Series", verbose_name="系列", on_delete=models.DO_NOTHING)
    points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    progress = models.CharField(max_length=32, default="0.00")


class PointDetail(models.Model):
    """
    得积分的记录
    """
    user = models.ForeignKey("User", verbose_name="用户", on_delete=models.DO_NOTHING)
    article = models.ForeignKey("Article", verbose_name="文章", on_delete=models.DO_NOTHING)
    point = models.IntegerField(default=0, verbose_name="积分")
    time = models.DateTimeField(auto_now_add=True, verbose_name="完成时间")  # 什么时候完成的
