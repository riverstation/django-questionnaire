import json

from django.http.response import HttpResponse


def json_response(data):
    """
    # 
    """
    result_dict = data
    return HttpResponse(json.dumps(result_dict), content_type="application/json")


def params_error(error):
    """
    # 
    """
    result_dict = error
    return HttpResponse(json.dumps(result_dict), content_type="application/json", status=422)


def not_authenticated():
    """
    # 
    """

    result_dict = {
        'authenticated': '没有登录'
    }
    return HttpResponse(json.dumps(result_dict), content_type="application/json", status=401)


def permission_denied():
    """
    #
    """
    result_dict = {
        'permission': "没有权限"
    }
    return HttpResponse(json.dumps(result_dict), content_type="application/json", status=403)


def server_error():
    """
    # 
    """
    result_dict = {
        'server': '服务器发生错误'
    }
    return HttpResponse(json.dumps(result_dict), content_type="application/json", status=500)


def method_not_allowed():
    """
    # 
    """
    result_dict = {
        'method': '方法不支持'
    }
    return HttpResponse(json.dumps(result_dict), content_type="application/json", status=405)
