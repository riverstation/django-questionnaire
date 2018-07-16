"""
# 通用接口
- 注册　
- 登录 
- 获取注册码  
- 更新用户信息  
- 获取用户信息  
- 退出
"""

import json
import random
from datetime import datetime, timedelta, date
import uuid
import os

from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from Question.models import *
from Api.resources import *

class RegistCode(Rest):
    """
    # 获取注册码
    """

    def get(self, request, *args, **kwargs):
        # 生成注册码
        regist_code = random.randint(10000, 99999)
        # 保存注册码
        request.session['regist_code'] = regist_code
        # 把返回的数据转化为json字符串
        result_dict = {
            'regist_code': regist_code
        }
        return json_response(result_dict)


class UserResource(Rest):
    """
    # 用户资源
    """

    def get(self, request, *args, **kwargs):
        # 判断用户是否登录
        if request.user.is_authenticated:
            # 判断用户类型
            user = request.user
            # 判断是否是客户
            if hasattr(user, 'customer'):
                customer = user.customer
                # 构建结果字典
                data = dict()
                data['user_id'] = user.id
                data['company_name'] = customer.company_name
                data['address'] = customer.address
                data['phone'] = customer.phone
                data['industry'] = customer.industry
                data['web_site'] = customer.web_site
                data['uscc'] = customer.uscc
                # 把日期对象转化为字符串
                data['create_date'] = datetime.strftime(
                    customer.create_date, '%Y-%m-%d')
                # 把图片保存的名字取出来
                data['logo'] = customer.logo.savename
                data['regist_amount'] = customer.regist_amount
                data['corporation'] = customer.corporation
                data['wechat'] = customer.wechat
                data['email'] = customer.email
                data['employee_numbers'] = customer.employee_numbers
                data['business_nature'] = customer.business_nature
                data['business_scope'] = customer.business_scope
                data['description'] = customer.description
                data['stock_code'] = customer.stock_code
            elif hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                data = dict()
                data['user_id'] = user.id
                data['name'] = userinfo.name
                data['gender'] = userinfo.gender
                # 把出身日期转化为字符串
                data['birthday'] = datetime.strftime(
                    userinfo.birthday, '%Y-%m-%d')
                data['marital_status'] = userinfo.marital_status
                data['mobile'] = userinfo.mobile
                data['qq'] = userinfo.qq
                data['wechat'] = userinfo.wechat
                data['job'] = userinfo.job
                data['address'] = userinfo.address
                data['email'] = userinfo.email
                # 把图片保存的名字取出来
                data['photo'] = userinfo.photo.savename
                data['education'] = userinfo.education
                data['major'] = userinfo.major
            elif hasattr(user, 'admin'):
                admin = user.admin
                data = dict()
                data['user_id'] = user.id
                data['name'] = admin.name
                data['job_id'] = admin.job_id
            else:
                return params_error({"user": "没有用户类型"})
            # 将数据返回给客户端
            return json_response(data)
        else:
            return not_authenticated()

    def put(self, request, *args, **kwargs):
        # 注册用户
        # 获取客户端上传的数据
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        ensure_password = data.get('ensure_password', '')
        regist_code = data.get('regist_code', '')
        category = data.get('category', '')
        # 获取session中保存的注册码
        session_regist_code = request.session.get('regist_code', 0)

        # 校验客户端数据
        # 验证用户名
        error = dict()
        if username:
            user_exist = User.objects.filter(username=username)
            if user_exist:
                error['username'] = "用户名已存在"
        else:
            error['username'] = '必须提供用户名'
        # 验证密码
        if len(password) < 6:
            error['password'] = '密码长度不可小于6位'
        if password != ensure_password:
            error['ensure_password'] = '密码不匹配'
        # 验证注册码
        if regist_code != str(session_regist_code):
            error['regist_code'] = '注册码不匹配'
        if error:
            return params_error(error)

        # 保存用户信息
        user = User()
        user.username = username
        user.set_password(password)
        user.save()

        # 保存相应的用户信息
        if category == 'customer':
            # 注册客户
            customer = Customer()
            customer.user = user
            customer.company_name = ''
            customer.address = ''
            customer.phone = ''
            customer.industry = ''
            customer.web_site = ''
            customer.uscc = ''

            customer.create_date = date(2018, 6, 21)
            # 创建图片对象
            logo = Image()
            logo.filename = ''
            logo.savename = ''
            logo.size = 0
            logo.save()
            customer.logo = logo

            customer.regist_amount = 0
            customer.corporation = ''
            customer.wechat = ''
            customer.email = ''
            customer.employee_numbers = 0
            customer.business_nature = ''
            customer.business_scope = ''
            customer.description = ''
            customer.stock_code = ''
            customer.save()

        else:
            # 注册用户
            userinfo = UserInfo()
            userinfo.user = user
            userinfo.name = ''
            userinfo.gender = ''
            userinfo.birthday = date(2018, 6, 21)
            userinfo.marital_status = ''
            userinfo.mobile = ''
            userinfo.qq = ''
            userinfo.wechat = ''
            userinfo.job = ''
            userinfo.address = ''
            userinfo.email = ''
            # 创建图片
            photo = Image()
            photo.filename = ''
            photo.savename = ''
            photo.size = 0
            photo.save()
            userinfo.photo = photo
            userinfo.education = ''
            userinfo.major = ''
            userinfo.save()

        return json_response({
            'id': user.id
        })

    def post(self, request, *args, **kwargs):
        # 判断是否登录
        if request.user.is_authenticated:
            user = request.user
            # 判断用户类型
            if hasattr(user, 'customer'):
                # 更新客户信息
                self.update_customer(request)
            elif hasattr(user, 'userinfo'):
                # 更新普通用户信息
                self.update_userinfo(request)
            elif hasattr(user, 'admin'):
                # 更新管理员信息
                self.update_admin(request)
            else:
                return params_error({"user": "没有用户类型"})
            return json_response({'msg':'更新成功'})
        else:
            return not_authenticated()

    def update_customer(self, request):
        data = request.POST
        files = request.POST_FILES
        customer = request.user.customer
        # 更新客户信息
        customer.company_name = data.get('company_name', '')
        customer.address = data.get('address', '')
        customer.phone = data.get('phone', '')
        customer.industry = data.get('industry', '')
        customer.web_site = data.get('web_site', '')
        customer.uscc = data.get('uscc', '')
        # 把%Y-%m-%d格式字符串转化为date对象
        customer.create_date = datetime.strptime(
            data.get('create_date', ''), "%Y-%m-%d")
        # 图片处理
        logo = files.get('logo', False)
        if logo:
            # 保存图片
            # 创建一个唯一文件名
            filename = str(uuid.uuid1())
            # 打开项目upload目下的文件
            logo_image = open(
                './upload/{filename}'.format(filename=filename), 'wb')
            # 把用户上传的文件写入打开的文件中
            for chunk in logo.chunks():
                logo_image.write(chunk)
            # 保存文件
            logo_image.close()
            # 更新客户的logo图片信息
            customer_logo = customer.logo
            customer_logo.savename = filename
            customer_logo.save()
        try:
            regist_amount = int(data['regist_amount'])
        except Exception:
            regist_amount = 0
        customer.regist_amount = regist_amount
        customer.corporation = data.get('corporation', '')
        customer.wechat = data.get('wechat', '')
        customer.email = data.get('email', '')
        try:
            employee_numbers = int(data['employee_numbers'])
        except Exception:
            employee_numbers = 0
        customer.employee_numbers = employee_numbers
        customer.business_nature = data.get('business_nature', '')
        customer.business_scope = data.get('business_scope', '')
        customer.description = data.get('description', '')
        customer.stock_code = data.get('stock_code', '')

        customer.save()

    def update_userinfo(self, request):
        data=request.POST
        files=request.POST_FILES
        userinfo=request.user.userinfo 

        userinfo.name=data.get('name','')
        userinfo.gender=data.get('gender','')
        # 把%Y-%m-%d格式字符串转化为date对象
        userinfo.birthday=datetime.strptime(data.get('birthday',''),"%Y-%m-%d")
        userinfo.marital_status=data.get('marital_status','')
        userinfo.mobile=data.get('mobile','')
        userinfo.qq=data.get('qq','')
        userinfo.wechat=data.get('wechat','')
        userinfo.job=data.get('job','')
        userinfo.address=data.get('address','')
        userinfo.email=data.get('email','')
        # 图片处理
        photo = files.get('photo', False)

        if photo:
            # 保存图片
            # 创建一个唯一文件名
            filename = str(uuid.uuid1())
            # 打开项目upload目下的文件
            photo_image = open(
                './upload/{filename}'.format(filename=filename), 'wb')
            # 把用户上传的文件写入打开的文件中
            for chunk in photo.chunks():
                photo_image.write(chunk)
            # 保存文件
            photo_image.close()
            # 更新客户的photo图片信息
            userinfo_photo = userinfo.photo
            userinfo_photo.savename = filename
            userinfo_photo.save()

        userinfo.education=data.get('education','')
        userinfo.major =data.get('major','')

        userinfo.save()

    def update_admin(self, request):
        data=request.POST 
        admin=request.user.admin 
        admin.name=data.get('name','')
        admin.job_id=data.get('job_id','')
        admin.save()


class Session(Rest):
    def put(self,request,*args,**kwargs):
        data=request.PUT
        username=data.get('username','')
        password=data.get('password','')
        # 判断用户是否存在
        user=authenticate(username=username,password=password)
        if user:
            login(request,user)
        else:
            return params_error({
                'error':"用户名或密码错误"
            })
        return json_response({'msg':"登录成功"})
    
    def delete(self,request,*args,**kwargs):
        logout(request)
        return json_response({'msg':"退出成功"})