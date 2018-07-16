"""
# 模型
- 客户
- 问卷
- 审核批注
- 管理员
- 问题
- 问题选项
- 用户
- 参与问卷
- 问卷答案
"""
from django.db import models
from django.contrib.auth.models import User

class Image(models.Model):
    filename = models.CharField(max_length=128, help_text="文件名")
    savename = models.CharField(max_length=128, help_text="保存时的文件名")
    size = models.IntegerField(help_text="文件大小")

# request.user  User
# user.customer


class Customer(models.Model):
    """
    # 客户模型
    """
    user = models.OneToOneField(User, help_text="系统登录用户")
    company_name = models.CharField(max_length=128, help_text="公司名")
    address = models.CharField(max_length=128, help_text="公司地址")
    phone = models.CharField(max_length=32, help_text="座机")
    industry = models.CharField(max_length=16, help_text="行业")
    web_site = models.CharField(max_length=128, help_text="网址")
    uscc = models.CharField(max_length=128, help_text="统一社会信用代码")
    create_date = models.DateField(help_text="创建时间")
    logo = models.OneToOneField('Image', help_text="logo")
    regist_amount = models.IntegerField(help_text="注册资金")
    corporation = models.CharField(max_length=128, help_text="法人")
    wechat = models.CharField(max_length=128, help_text="微信公众账号")
    email = models.CharField(max_length=128, help_text="邮箱")
    employee_numbers = models.IntegerField(help_text="企业人数")
    business_nature = models.CharField(max_length=128, help_text="企业性质")
    business_scope = models.TextField(help_text="经营范围")
    description = models.TextField(help_text="公司简介")
    stock_code = models.CharField(max_length=32, default="", help_text="股票代码")


# user.userinfo
class UserInfo(models.Model):
    """
    # 用户
    """
    user = models.OneToOneField(User, help_text="系统登录用户")
    name = models.CharField(max_length=32, help_text="姓名")
    gender = models.CharField(max_length=32, help_text="性别")
    birthday = models.DateField(help_text="出生日期")
    marital_status = models.CharField(max_length=32, help_text="婚姻状况")
    mobile = models.CharField(max_length=32, help_text="手机号码")
    qq = models.CharField(max_length=32, help_text="QQ")
    wechat = models.CharField(max_length=128, help_text="微信")
    job = models.CharField(max_length=128, help_text="工作")
    address = models.CharField(max_length=128, help_text="地址")
    email = models.CharField(max_length=128, help_text="邮箱")
    photo = models.OneToOneField("Image", help_text="头像")
    education = models.CharField(max_length=128, help_text="学历")
    major = models.CharField(max_length=128, help_text='专业')


class Questionnaire(models.Model):
    """
    # 问卷模型
    """
    customer = models.ForeignKey('Customer', help_text='问卷所属客户')
    title = models.CharField(max_length=128, help_text="标题")
    create_date = models.DateField(help_text="创建时间")
    expire_date = models.DateField(help_text="截止时间")
    quantity = models.IntegerField(help_text="问卷总数")
    left = models.IntegerField(help_text="剩余问卷数量")
    state = models.IntegerField(
        default=0, help_text="0-->草稿状态,1-->待审核状态,2-->审核失败,3-->审核通过,4-->已发布")


class Question(models.Model):
    """
    # 问题
    """
    questionnaire = models.ForeignKey('Questionnaire', help_text="问题所属的问卷")
    title = models.CharField(max_length=128, help_text="题目")
    is_checkbox = models.BooleanField(help_text="是否多选")


class Item(models.Model):
    """
    # 选项
    """
    question = models.ForeignKey('Question', help_text="题目")
    content = models.CharField(max_length=128, help_text="选项内容")


class QuestionnaireComment(models.Model):
    """
    # 审核批注
    """
    questionnaire = models.ForeignKey('Questionnaire', help_text="审核的问卷")
    create_date = models.DateField(auto_now=True, help_text="审核时间")
    comment = models.TextField(help_text="审核内容")
    admin = models.ForeignKey('Admin', help_text="审核人")


class Admin(models.Model):
    """
    # 管理员
    """
    user = models.OneToOneField(User, help_text="登录账号")
    name = models.CharField(max_length=32, help_text="姓名")
    job_id = models.CharField(max_length=32, help_text="工号")


class JoinQuestionnaire(models.Model):
    """
    # 问卷参与
    """
    questionnaire = models.ForeignKey('Questionnaire', help_text="参与的问卷")
    userinfo = models.ForeignKey('UserInfo', help_text="用户")
    create_date = models.DateField(help_text="参与时间")
    is_done = models.BooleanField(help_text="是否完成该问卷")


class AnswerQuestionnaire(models.Model):
    """
    # 问卷答案
    """
    userinfo = models.ForeignKey('UserInfo', help_text="用户")
    item = models.ForeignKey('Item', help_text="选项")

