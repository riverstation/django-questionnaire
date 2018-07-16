import json
from datetime import datetime 
import random


from django.http.multipartparser import MultiPartParser
from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponse

from Api.utils import *

class ConvertData(MiddlewareMixin):

    def process_request(self, request):
        method = request.method
        # 假如请求方法是get,那么不需要解析请求体
        if method == 'GET':
            return None
        if 'application/json' in request.content_type:
            # 解析json字符串,把json字符串转化为python的字典
            try:
                # 将字符串转化为字典
                data = json.loads(request.body)
            except Exception:
                # 如果解析失败,那么通知客户端数据格式不正确
                return params_error({
                    "data":"不是正确的json字符串"
                })
        elif 'multipart/form-data' in request.content_type:
            # 解析表单数据,因为django只对post方式提交的表单数据进行了解析,
            # 所以要手动解析其他方式提交的表单数据
            # 这里解析出来的data是普通的input数据,files是通过表单上传的文件
            data, files = MultiPartParser(
                request.META, request, request.upload_handlers).parse()
            # 给request对象设置属性,方便业务处理函数读取请求的数据
            # 例如使用put上传了文件,那么业务处理函数通过request.PUT_FILES获取上传的文件
            setattr(request, request.method+'_FILES', files)
        else:
            return params_error({
                "data":'不支持该数据类型'
            })
        # 把请求的数据,设置为request的一个属性
        # 例如要获取delete方法携带的请求数据,那么通过reqquest.DELETE获取请求的数据
        setattr(request, request.method, data)

