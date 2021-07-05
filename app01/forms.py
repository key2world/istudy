# 将forms都放到一个文件中
from django import forms
from django.core.exceptions import ValidationError  # 校验器错误
import hashlib  # 作加密
from app01 import models
from captcha.fields import CaptchaField  # 验证码


class BSForm(forms.ModelForm):
    """
    拥有bootstrap的样式  公共部分提取
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定义操作
        for field in self.fields.values():  # 有序字典，这个字典里的值所对应的就是字段的对象
            field.widget.attrs["class"] = "form-control"  # field.widget拿到插件对象，.attrs在拿到属性


# class Register(forms.Form):  # 普通form写法 一个一个写input框 比较麻烦
class Register(forms.ModelForm):  # ModelForm比较快速的写法 不用自己定义字段
    # username = forms.CharField()  # 不用自己定义字段

    # 因为是自定义字段了 error_message也要自己定义
    password = forms.CharField(error_messages={"required": "必填项", "min_length": "密码要不少于六位哟"},
                               widget=forms.PasswordInput(attrs={"placeholder": "密码", "type": "password"}), label="密码",
                               min_length=6)  # 自定义字段  会以自定义的字段为主
    # attrs={"placeholder": "密码", "type": "password"}是为了前端input框中有提示
    re_pwd = forms.CharField(error_messages={"required": "必填项"},
                             widget=forms.PasswordInput(attrs={"placeholder": "确认密码", "type": "password"}),
                             label="确认密码",
                             min_length=6)  # 自定义字段
    captcha = CaptchaField(label="验证码", error_messages={"required": "必填项", "invalid": "验证码错误"},)

    class Meta:  # 在表的参数中也有这种写法
        # 我要去根据一个model帮我去生成这个字段 而不是我在这里一个一个去写
        # 我要去根据User（表名）的这个model帮我生成对应的form里边要写的这些字段
        model = models.User  # 要注意别把model写错为models

        # 你根据这个model里面那些字段去生成input框
        fields = '__all__'  # 所有的字段    # ['username', 'password' ]  # 自己指定

        # 排除那些字段不要
        exclude = ['last_time', "is_active"]  # 除了last_time不要在的全部都要

        # 修改提示信息label  一种方法  也可以在models中 字段中加verbose_name参数
        # labels = {
        #     "username": "用户名",
        # }

        # 修改input框类型 widget
        widgets = {
            'username': forms.TextInput(attrs={"placeholder": "用户名", "autocomplete": "off"}),
            # "autocomplete": "off" 不要自动提示
            # 'company': forms.Select(),  # 选择框
            'position': forms.TextInput(attrs={"placeholder": "职位"}),
            'phone': forms.TextInput(attrs={"placeholder": "手机号"}),
        }

        # 错误的提示信息
        error_messages = {
            "username": {
                "required": "必填项",
                "unique": "用户名已存在",  # User with this 用户名 already exists. 在数据库中是unique所以
            },
            'position': {
                "required": "必填项",
            },
            'phone': {
                "required": "必填项",
            },
            'company': {
                "required": "必填项",
            },
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        print("-" * 40)
        print(username)
        if len(username.strip()) < 4:
            raise ValidationError("用户名不能少于4位哟")

        for i in username:
            if u'\u4e00' <= i <= u'\u9fff':
                raise ValidationError("用户名不能为汉字哟")
        return username

    def clean_phone(self):
        import re
        phone = self.cleaned_data.get("phone")
        if re.findall(r"^1[3-9]\d{9}$", phone):
            # 手机号格式正确
            return phone
        raise ValidationError("手机号格式不正确")

    def clean(self):
        self._validate_unique = True  # 数据库要校验用户名等之类不可以重复的字段是否唯一（相比较Form多出的特点）
        password = self.cleaned_data.get("password", "")  # 为两个密码都没有填写的情况
        re_pwd = self.cleaned_data.get("re_pwd")
        if password == re_pwd:
            # 密码和确认密码一致 返回全部字段
            # 给密码加密 可以在局部钩子中加密也可以在全局钩子中加密  在局部钩子中加密需要两次（密码和确认密码） 所以在全局钩子中加密
            md5 = hashlib.md5()  # 生成md5
            md5.update(password.encode("utf-8"))  # 做更新
            print(md5.hexdigest())  # 加密后的密码
            self.cleaned_data["password"] = md5.hexdigest()
            return self.cleaned_data
        self.add_error("re_pwd", "两次密码不一致")
        raise ValidationError("两次密码不一致")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定义操作
        field = self.fields['company']
        # print(field)  # 字段
        # print(field.choices)
        choices = field.choices
        choices[0] = ("", "请选择公司")
        field.choices = choices


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = "__all__"
        exclude = ["detail"]
        # 修改input框类型 widget  比较复杂
        # widgets = {
        #     "title": forms.TextInput(attrs={"class": "form-control"})
        # }

    def __init__(self, request, *args, **kwargs):
        # 获取到用户传来的其他参数 request 不要往下面的__init__方法传了
        super().__init__(*args, **kwargs)

        # 自定义操作 之前修改字段所对应的choise参数
        for field in self.fields.values():  # 有序字典，这个字典里的值所对应的就是字段的对象
            field.widget.attrs["class"] = "form-control"  # field.widget拿到插件对象，.attrs在拿到属性

        # 修改choices的参数
        # print(list(self.fields['author'].choices))  # 查看字段author的choice参数
        self.fields['author'].choices = [(request.user_obj.id, request.user_obj.username)]


class ArticleDetailForm(forms.ModelForm):
    class Meta:
        model = models.ArticleDetail
        fields = "__all__"


class CategoryForm(BSForm):
    class Meta:
        model = models.Category
        fields = "__all__"
        # widgets = {  # 修改input类型
        #     "title": forms.TextInput(attrs={"class": "form-control"})
        # }


class SeriesForm(BSForm):
    class Meta:
        model = models.Series
        fields = "__all__"
