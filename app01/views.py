from django.shortcuts import render, redirect
from app01 import models
import hashlib
from app01.forms import Register, ArticleForm, ArticleDetailForm, CategoryForm, SeriesForm
from utils.pagination import Pagination
from captcha.models import CaptchaStore  # 导入captcha_captchastore表


# Create your views here.
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 这里因为注册时写入数据的是加密的密码，所以这里的密码在查询数据库的时候也要加密查询
        md5 = hashlib.md5()  # 创建md5对象
        md5.update(password.encode("utf-8"))  # 作更新就好了
        # print(md5.hexdigest())  # 加密后的密码
        user_obj = models.User.objects.filter(username=username, password=md5.hexdigest(),
                                              is_active=True).first()  # is_active=True是否删除账号
        if user_obj:
            # 登录成功
            # 保存登录状态（session） 登录名
            request.session["is_login"] = True
            request.session["username"] = user_obj.username
            request.session["pk"] = user_obj.pk

            # 判断是在哪一步要求登录的 登录成功在返回到那个页面
            if request.GET.get("url"):
                return redirect(request.GET.get("url"))
            return redirect("index")
        # 登录失败
        error = "用户名或密码错误"
    return render(request, "login.html", locals())


def logout(request):
    request.session.delete()
    if request.GET.get("url"):
        return redirect(request.GET.get("url"))
    return redirect("index")


def register(request):
    form_obj = Register()  # 实例化ModelForm
    if request.method == "POST":
        form_obj = Register(request.POST, request.FILES)  # FILES是头像
        if form_obj.is_valid():
            # 注册成功
            # 方法一 将数据加入到数据库中
            # print(request.POST)  # 查看数据（包含提交的数据）  有额外的字段
            # print(form_obj.cleaned_data)  # 查看数据（包含清洗过的数据）  仅有定义的字段  选择这个将数据写进数据库
            # form_obj.cleaned_data.pop("re_pwd")  # 将自己定义的字段删除，应为要加入到数据库，数据库中没有这个字段
            # models.User.objects.create(**form_obj.cleaned_data)  # **打散字典，相当于传入为key=value这种数据类型

            # 方法二 将数据加到数据库中
            # form_obj和model已经有关系了
            form_obj.save()  # 直接保存到数据库中将数据
            return redirect("login")  # 跳转到登录页面
    return render(request, "register.html", {"form_obj": form_obj})


# 检查用户名是否重复
def check_user_name(request):
    username = request.GET.get("username")

    print("-" * 40)
    print(username)
    if len(username.strip()) < 4:
        return JsonResponse({"username": "short"})  # 用户名太短

    for i in username:
        if u'\u4e00' <= i <= u'\u9fff':
            return JsonResponse({"username": "chinese"})  # 中文错误

    user_obj = models.User.objects.filter(username=username)

    if user_obj:
        return JsonResponse({"username": True})
    return JsonResponse({"username": False})


from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie


# 需要加到视图上 csrf_protect 该视图需要进行csrf校验
# 需要加到视图上 ensure_csrf_cookie 确保有cookies

# csrf_exempt免除csrf校验
# 检查密码是否设置正确
# @csrf_exempt  # csrf_exempt免除csrf校验
def check_password(request):
    password = request.POST.get("password")
    try:
        if len(password) < 6:
            return JsonResponse({"password": False})
        else:
            return JsonResponse({"password": True})
    except:
        return JsonResponse({"password": False})


# 检查两次密码输入是否一致
def check_re_pwd(request):
    password = request.POST.get("password")
    re_pwd = request.POST.get("re_pwd")
    # print(password)
    # print(re_pwd)
    if re_pwd == "":
        return JsonResponse({"password": 1})
    elif re_pwd == password:
        return JsonResponse({"password": 2})
    return JsonResponse({"password": 3})


'''
验证码生成的原理:
django-simple-captcha并没有使用session对验证码进行存储，而是使用了数据库，
首先生成一个表 captcha_captchastore
这个隐藏字段就是hashkey的值，django将hashkey传给页面以hidden的形式存在，提交表单时 hashkey与 
输入的验证码 一起post到服务器，此时服务器验证 captcha_captchastore表中 hashkey 对应的 response 
是否与 输入的验证码一致，如果一致则正确，不一致返回错误。 
'''


# 检查验证码是否正确
def check_captcha(request):
    if request.is_ajax():
        # 如果是ajax请求
        # 前端输入的验证码 和数据表中存的response 是否一致
        # hashkey 找到对象的response
        captcha = CaptchaStore.objects.filter(response=request.GET.get("response"),
                                              hashkey=request.GET.get("hashkey"))
        if captcha:
            json_data = {"status": 1}
        else:
            json_data = {"status": 0}
        return JsonResponse(json_data)
    else:
        # 如果不是ajax请求
        return redirect("index")


def index(request):
    # 查询所有的文章
    all_article = models.Article.objects.filter(publish_status=True).order_by("-create_time")
    # obj = models.User.objects.filter(pk=request.session.get("pk")).first() # 查找到当前用户的那行数据
    # print(obj.avatar.url)  # 获取到图片访问地址，不是数据库中的地址

    # 分页
    pagination = Pagination(request, len(all_article), 3)

    return render(request, "index.html",
                  {"all_article": all_article[pagination.start:pagination.end], "page_html": pagination.page_html})


def article(request, pk):
    # 查询出文章内容
    article_obj = models.Article.objects.get(pk=pk)
    return render(request, "article.html", {"article_obj": article_obj})


def backend(request):
    return render(request, "dashboard.html")


from django.db.models import Q


def get_query(request, field_list):
    # 字段中查询不了时间是utc的问题
    # 传入要一个列表["title", "detail__content"]  就是要搜索的字段名 ， 返回一个Q对象
    # 先创建一个Q对象
    q = Q()
    q.connector = "OR"  # 就是子Q中的连接方式
    query = request.GET.get("query", "")
    # Q(Q(title__contains=query) | Q(detail__content=query))  # 最外边的Q包含着 里边的两个Q
    # q.children.append(Q(title__contains=query))  # 可以给最外边的Q传入进去子Q  关键字传入
    # q.children.append(("title__contains",query))  # 和上边一模一样  位置传入
    for field in field_list:
        q.children.append(("{}__contains".format(field), query))
    return q, query


# 展示文章列表
def article_list(request):
    # 应该是获取当前用户的文章 现在文章比较少全部都获取出来了
    # all_article = models.Article.objects.all()
    # 当前用户的文章
    # all_article = request.user_obj.article_set.all()  # 特殊写法
    # author 在文章表中是外键 所以查询中可以使用author对象
    # all_article = models.Article.objects.filter(author=request.user_obj)

    # 模糊搜索
    query = request.GET.get("query", "")  # url上的参数
    # all_article = models.Article.objects.filter(author=request.user_obj).filter(
    #     Q(title__contains=query) | Q(detail__content=query))

    q, query = get_query(request, ["title", "detail__content"])
    all_article = models.Article.objects.filter(q, author=request.user_obj)

    # 分页
    pagination = Pagination(request, all_article.count())
    return render(request, "article_list.html",
                  {"all_article": all_article[pagination.start:pagination.end], "page_html": pagination.page_html,
                   "query": query})


# 新增文章
def article_add(request):
    # 第一种方法 修改from中的choices参数
    # 直接往forms中传入request form_obj = ArticleForm(request)
    # 第二种方法 自己给instance实例对象赋值
    # obj = models.Article(author=request.user_obj)  # 自己实例化一个对象， 自己给author赋值，别的让用户填
    # form_obj = ArticleForm(request, instance=obj)  # 然后传入参数

    # instance 是去构造一个，指定model里边（就是modelform里边对应的models.的类）的一个对象

    form_obj = ArticleForm(request)
    article_detail_form_obj = ArticleDetailForm()
    if request.method == "POST":
        form_obj = ArticleForm(request, request.POST)
        article_detail_form_obj = ArticleDetailForm(request.POST)
        if form_obj.is_valid() and article_detail_form_obj.is_valid():
            # 将前端用户输入的数据保存到数据库
            # form_obj.save()  数据不够这种方法不行
            # 第一步，先将文章详情插入到数据库  得到对象
            # detail = request.POST.get("detail")  # 通过name拿到文章内容
            # detail_obj = models.ArticleDetail.objects.create(content=detail)  # 插入到数据库中
            # 第二步，往文章表里插入内容
            # print(form_obj.cleaned_data)

            # 将文章详情保存
            detail_obj = article_detail_form_obj.save()
            form_obj.cleaned_data["detail_id"] = detail_obj.pk  # 将短缺的数据加到字典中
            models.Article.objects.create(**form_obj.cleaned_data)  # 将字典数据打散 传入数据库中

            # 方法二:从上边第二步开始
            # form_obj.instance.detail_id = detail_obj.pk
            # form_obj.save()
            return redirect("article_list")
    return render(request, "article_add.html",
                  {"form_obj": form_obj, "article_detail_form_obj": article_detail_form_obj})


# 编辑文章
def article_edit(request, pk):
    obj = models.Article.objects.filter(pk=pk).first()
    # instance 内部如果是自己不生成，不传值的时候 自己会拿到一个空的，在这里是可以传入实例对象的，
    # 这个对象就是ModelForm里所指定的model所对应的那个对象
    form_obj = ArticleForm(request, instance=obj)
    article_detail_form_obj = ArticleDetailForm(instance=obj.detail)  # 文章详情的那个

    if request.method == "POST":
        form_obj = ArticleForm(request, request.POST, instance=obj)
        article_detail_form_obj = ArticleDetailForm(request.POST, instance=obj.detail)

        if form_obj.is_valid() and article_detail_form_obj.is_valid():
            # 方法一：自己的笨办法
            # # 有两张表要存储东西 先将文章详情存入表中，在存储文章
            # detail_obj = models.ArticleDetail.objects.filter(pk=obj.detail_id).first()
            # detail_obj.content = request.POST.get("detail")
            # detail_obj.save()   # 保存文章详情
            #
            # # form_obj.instance.detail.content = request.POST.get("detail")
            # # 这样在数据库中修改了，但是么有保存修改的那张表  所以数据不会存到数据库中
            #
            # form_obj.save()  # 对另一张表修改后的保存（保存文章的信息）

            # 方法二：
            # form_obj.instance.detail.content = request.POST.get("detail")  # 修改文章详情
            # form_obj.instance.detail.save()  # 保存文章详情表

            article_detail_form_obj.save()  # 保存文章详情表
            form_obj.save()  # 保存文章信息的表  form_obj.instance.save()也可

            if request.GET.get("url"):
                return redirect(request.GET.get("url"))
            return redirect(article_list)
    return render(request, "article_edit.html",
                  {"form_obj": form_obj, "article_detail_form_obj": article_detail_form_obj})


# 删除文章
def article_delete(request, pk):
    # 两种删除方法
    # 假删除就是把显示状态调整
    # 真删除将数据库中的数据删除
    models.Article.objects.get(pk=pk).delete()
    return redirect(article_list)


# 自己造数据
users = [{"name": "alex-{}".format(i), "pwd": "123456"} for i in range(1, 446)]


# 分页
def user_list(request):
    """分页的源码"""
    # try:
    #     page = int(request.GET.get("page", 1))  # 如果url上没有这个参数，则默认值1
    #     if page <= 0:
    #         page = 1
    # except Exception:
    #     page = 1
    #
    # # 每页显示的数据条数  内容的多少
    # pre_num = 10
    #
    # # 就是显示的内容
    # # 切片的起始值
    # start = (page - 1) * pre_num
    # # 切片的终止值
    # end = page * pre_num
    #
    # # 总的页码数
    # # total_num = len(users) / pre_num
    # # divmod 有两个返回值，分别是整除的结果，取余的结果
    # total_num, more = divmod(len(users), pre_num)
    # if more:
    #     total_num += 1
    #
    # # 要显示的页码数
    # max_show = 10
    # # 页码条中间的那个数
    # half_show = max_show // 2
    #
    # # 如果总的页码数还没有要显示的页码数多 就显示总的页码数
    # if total_num <= max_show:
    #     # 页码的起始值
    #     page_start = 1
    #     # 页码的终止值
    #     page_end = total_num
    # else:
    #     # 就是为了页码条永远等于要显示的页码数
    #     page_start = page - half_show
    #     page_end = page + half_show - 1
    #     if page_start <= 0:
    #         page_start = 1
    #         page_end = max_show
    #
    #     elif page_end > total_num:
    #         page_start = total_num - max_show + 1  # 小bug 不然就会出现11个页码数
    #         page_end = total_num
    # page_list = []
    # if page == 1:
    #     page_list.append(
    #         '<li class="disabled"><a><span aria-hidden="true">&laquo;</span></a></li>')  # 如果上一页没有了 就把这个标签禁用掉
    # else:
    #     page_list.append(
    #         '<li><a href="?page={}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
    #             page - 1))  # 上一页
    #
    # for i in range(page_start, page_end + 1):
    #     if i == page:  # 当前页码特殊显示
    #         page_list.append('<li class="active"><a href="?page={}">{}</a></li>'.format(i, i))
    #     else:
    #         page_list.append('<li><a href="?page={}">{}</a></li>'.format(i, i))
    # if page == total_num:
    #     page_list.append(
    #         '<li class="disabled"><a><span aria-hidden="true">&raquo;</span></a></li>')  # 没有下一页禁用标签
    # else:
    #     page_list.append(
    #         '<li><a href="?page={}" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'.format(
    #             page + 1))  # 下一页
    #
    # page_html = "".join(page_list)

    pagination = Pagination(request, len(users), )
    return render(request, "user_list.html",
                  {"users": users[pagination.start:pagination.end], "page_html": pagination.page_html})


# 分类列表
def category_list(request):
    q, query = get_query(request, ["title", "pk"])
    all_categories = models.Category.objects.all().filter(q)
    pagination = Pagination(request, len(all_categories), 5)  # 分页
    return render(request, "category_list.html",
                  {"all_categories": all_categories[pagination.start:pagination.end], "query": query,
                   "page_html": pagination.page_html})


# 新增分类
def category_add(request):
    form_obj = CategoryForm()
    if request.method == "POST":
        form_obj = CategoryForm(request.POST)
        if form_obj.is_valid():
            # 校验成功 存放到数据库
            form_obj.save()
            return redirect("category_list")

    return render(request, "category_add.html", {"form_obj": form_obj})


# 修改分类
def category_edit(request, pk):
    obj = models.Category.objects.filter(pk=pk).first()
    form_obj = CategoryForm(instance=obj)
    if request.method == "POST":
        form_obj = CategoryForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            if request.GET.get("url"):
                return redirect(request.GET.get("url"))
            return redirect("category_list")
    return render(request, "category_edit.html", {"form_obj": form_obj})


# 删除分类
def category_del(request, pk):
    models.Category.objects.filter(pk=pk).delete()
    return redirect("category_list")


from django.http.response import JsonResponse
from django.utils import timezone  # 将utc时间转换为当前时区的时间


# 评论
def comment(request):
    # print(request.GET.dict())  # 将QueryDict特殊字典转换为普通字典  方便传入数据库
    obj = models.Comment.objects.create(**request.GET.dict())  # **打散字典content="content"
    # print("-"*100)
    # print(obj.time)  # 刚从数据库中取出的时间utc时间
    # print(timezone.is_aware(obj.time))  # 测试这个时间是否具有时区信息
    # print(timezone.localtime(obj.time).strftime("%Y-%m-%d %H:%M:%S"))  # 转换时间
    pk = obj.id
    return JsonResponse(
        {"status": True, "time": timezone.localtime(obj.time).strftime("%Y-%m-%d %H:%M:%S"), "pk": pk})


def comment_del(request, pk):
    models.Comment.objects.filter(pk=pk).delete()

    return redirect(request.GET.get("url"))


# 系列
def series_list(request):
    q, query = get_query(request, ["title"])
    all_series = models.Series.objects.all().filter(q)
    pagination = Pagination(request, len(all_series), 5)  # 分页
    return render(request, "series_list.html",
                  {"all_series": all_series[pagination.start:pagination.end], "query": query,
                   "page_html": pagination.page_html})


def series_change(request, pk=None):
    obj = models.Series.objects.filter(pk=pk).first()  # pk=None  obj=>None
    form_obj = SeriesForm(instance=obj)
    if request.method == "POST":
        form_obj = SeriesForm(request.POST, instance=obj)
        if form_obj.is_valid():
            # print(form_obj.clean_data)  # 可以通过这个得到清洗过后的数据
            # form_obj.save()  # 完成了三件事
            # 新增了系列的对象
            form_obj.instance.save()
            obj = form_obj.instance  # 可以当做系列  form_obj(是Series类中的所有字段) 是Series的对象  .instance 可以拿到值
            # 保存了系列和文章的多对多关系
            obj.articles.set(form_obj.cleaned_data.get("articles"))  # [id],[对象]
            # 保存了系列和用户的多对多关系
            users = form_obj.cleaned_data.get("users")
            if not pk:  # 新增
                obj_list = []
                for user in users:
                    # models.UserSeries.objects.create(user_id=user.pk, series_id=obj.pk)  # 这个有几个用户就会插入几次 效率不高
                    obj_list.append(
                        models.UserSeries(user_id=user.pk, series_id=obj.pk))  # 自己实例化UserSeries对象  并没有往数据库做插入
                    # 和数据库是没有关系的 在内存里边生成UserSeries对象
                if obj_list:  # 一次性批量插入
                    models.UserSeries.objects.bulk_create(obj_list)  # 批量插入
            else:  # 编辑
                # 分三种情况
                # 新添加用户
                old = set(obj.users.all())
                new = set(users)
                add_users = new - old
                if add_users:
                    obj_list = []
                    for user in users:
                        obj_list.append(
                            models.UserSeries(user_id=user.pk, series_id=obj.pk))
                    if obj_list:  # 一次性批量插入
                        models.UserSeries.objects.bulk_create(obj_list)  # 批量插入
                # 删除用户
                del_users = old - new
                if del_users:
                    # 删除这个系列中  用户id在del_users中的数据
                    models.UserSeries.objects.filter(series_id=obj.pk, user_id__in=del_users).delete()
                # 用户没有变更  啥都不做
            return redirect("series_list")
    title = "编辑系列" if pk else "新增系列"
    return render(request, "series_change.html", {"form_obj": form_obj, "title": title})


def series_del(request, pk):
    models.Series.objects.filter(pk=pk).delete()
    return redirect("series_list")


# 个人信息
def profile(request):
    all_user_series = models.UserSeries.objects.filter(user=request.user_obj)
    # 查找当前登录用户的对象
    return render(request, "profile.html", {"all_user_series": all_user_series})


# 校验（注册用户名ajax校验）
def check(request):
    models.User.objects.filter(request.GET.get())


from django.db.models import F, Sum


# 积分
def point(request):
    # print(request.GET)
    # 插入得分记录

    # 确保不出现刷分
    # get_or_create() 获取或创建对象  如果数据库中这个对象就是获取  没有就是插入  返回值是 插入对象和True  或者 查询到的对象和False
    obj, creat = models.PointDetail.objects.get_or_create(**request.GET.dict())  # .dict将querydict转换为普通字典  插入到数据库
    # print(obj, creat)
    if creat:
        # 更新系列的进度
        query_set = models.UserSeries.objects.filter(user=request.user_obj, series__in=obj.article.series_set.all())
        # 加积分前计算每个系列的总积分
        # 根据系列series分组  求积分
        ret = query_set.values("series_id").annotate(total_points=Sum("series__articles__point"))
        for i in ret:
            # print(i)
            models.UserSeries.objects.filter(user=request.user_obj, series_id=i["series_id"]).update(
                total_points=i["total_points"])
        # 加积分
        # round() 保留浮点数小数点位数
        query_set.update(points=F("points") + obj.point,
                         progress=F("points") / F("total_points") * 100)

        # 这个用户 所看的这篇文章所对应的系列的记录
        # obj.article.series_set.all()  # 拿到当前阅读的这个文章所在的所有系列

        return JsonResponse({"status": True})
    return JsonResponse({"status": False})


def ceshi(request):
    return render(request, "test.html")


# 给别人展示的个人页面
def user_profile(request, pk):
    # print(pk, type(pk))
    return render(request, "user_profile.html", {"pk": pk})
