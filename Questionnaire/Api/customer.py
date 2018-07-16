from datetime import date, datetime, timedelta
import math

from Question.models import *
from Api.utils import *
from Api.resources import Rest
from Api.decorators import *


class CustomerQuestionnaire(Rest):
    @customer_required
    def get(self, request, *args, **kwargs):
        user = request.user
        customer = user.customer
        data = request.GET
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 10))
        start_id = int(data.get('start_id', 1))
        with_detail = data.get('with_detail', False)

        questionnaire = Questionnaire.objects.filter(
            id__gte=start_id, customer=customer)
        count = questionnaire.count()
        pages = math.ceil(count/limit) or 1
        if page > pages:
            page = pages
        # 取出对应页面的数据
        start = (page-1)*limit
        end = page*limit
        objs = questionnaire[start:end]
        # 构建响应数据
        result = dict()
        result['objs'] = []
        for obj in objs:
            # 构建
            questionnaire_dict = dict()
            questionnaire_dict['id'] = obj.id
            questionnaire_dict['title'] = obj.title
            questionnaire_dict['create_date'] = datetime.strftime(
                obj.create_date, '%Y-%m-%d')
            questionnaire_dict['expire_date'] = datetime.strftime(
                obj.expire_date, '%Y-%m-%d')
            questionnaire_dict['quantity'] = obj.quantity
            questionnaire_dict['left'] = obj.left
            questionnaire_dict['state'] = obj.state

            if with_detail == 'true':
                # 构建问卷下问题列表
                questionnaire_dict['questions'] = []
                for question in obj.question_set.all():
                    question_dict = dict()
                    question_dict['id'] = question.id
                    question_dict['title'] = question.title
                    question_dict['is_checkbox'] = question.is_checkbox
                    # 构建问题下选项列表
                    question_dict['items'] = []
                    for item in question.item_set.all():
                        item_dict = dict()
                        item_dict['id'] = item.id
                        item_dict['content'] = item.content

                        question_dict['items'].append(item_dict)

                    questionnaire_dict['questions'].append(question_dict)
                # 构建批注信息
                questionnaire_dict['comments'] = []
                for comment in obj.questionnairecomment_set.all():
                    comment_dict = dict()
                    comment_dict['id'] = comment.id
                    comment_dict['create_date'] = datetime.strftime(
                        comment.create_date, "%Y-%m-%d")
                    comment_dict['comment'] = comment.comment

                    questionnaire_dict['comments'].append(comment_dict)

            result['objs'].append(questionnaire_dict)
        return json_response(result)
    
    @customer_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        user = request.user
        questionnaire = Questionnaire()
        questionnaire.customer = user.customer
        questionnaire.title = data.get('title', '')

        # 把'%Y-%m-%d'格式字符串转化为时间
        create_date = datetime.strptime(
            data.get('create_date', ''), '%Y-%m-%d')
        questionnaire.create_date = create_date

        expire_date = datetime.strptime(
            data.get('expire_date', ''), '%Y-%m-%d')
        questionnaire.expire_date = expire_date

        try:
            quantity = int(data['quantity'])
        except Exception:
            quantity = 100

        questionnaire.quantity = quantity
        questionnaire.left = quantity
        questionnaire.state = 0
        questionnaire.save()
        return json_response({
            'id': questionnaire.id
        })
    @customer_required
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST
        customer = user.customer
        questionnaire_id = data.get('id', 0)
        # 找出当前客户下的问卷,并且该问卷是未发布状态
        questionnaire_exist = Questionnaire.objects.filter(
            id=questionnaire_id, customer=customer, state__in=[0, 1, 2, 3])
        if questionnaire_exist:
            questionnaire = questionnaire_exist[0]
        else:
            return params_error({'id': "找不到该问卷,或者该问卷已发布"})
        # 更新问卷信息
        questionnaire.title = data.get('title', '')
        # 把%Y-%m-%d格式字符串转化为时间
        create_date = datetime.strptime(
            data.get('create_date', ''), '%Y-%m-%d')
        questionnaire.create_date = create_date

        expire_date = datetime.strptime(
            data.get('expire_date', ''), '%Y-%m-%d')
        questionnaire.expire_date = expire_date

        try:
            quantity = int(data['quantity'])
        except Exception:
            quantity = 100

        questionnaire.quantity = quantity
        questionnaire.left = quantity
        # 判断客户端提交的状态
        state = int(data.get('state', 0))
        if state >= 1:
            questionnaire.state = 1
        else:
            questionnaire.state = 0
        questionnaire.save()
        return json_response({
            'msg': '更新成功'
        })
    @customer_required
    def delete(self, request, *args, **kwargs):
        user = request.user
        data = request.DELETE
        customer = user.customer
        ids = data.get('ids', [])
        # 找出可以被删除的问卷
        questionnaire_to_delete = Questionnaire.objects.filter(
            id__in=ids, customer=customer, state__in=[0, 1, 2, 3])
        # 把将要被删除的问卷id取出来
        deleted_ids = [obj.id for obj in questionnaire_to_delete]
        # 删除问卷
        questionnaire_to_delete.delete()
        return json_response({
            'deleted_ids': deleted_ids
        })


class CustomerQuestion(Rest):
    @customer_required
    def put(self, request, *args, **kwargs):
        """
        # 创建问题
        {
            "questionnaire_id":1,//问卷id
            "question":{
                "title":"问题" ,//问题标题
                "is_checkbox":false,//是否为多选
                "items":["选项1",...]//问题选项
            }
        }
        """
        user = request.user
        data = request.PUT
        customer = user.customer
        # 找出问卷
        questionnaire_id = data.get('questionnaire_id', '')
        questionnaire_exist = Questionnaire.objects.filter(
            id=questionnaire_id, customer=customer, state__in=[0, 1, 2, 3])
        if questionnaire_exist:
            questionnaire = questionnaire_exist[0]
        else:
            return params_error({
                'questionnaire_id': "问卷不存在,或者改问卷已发布"
            })
        # 创建问题
        # 客户端提交的问题数据格式
        # {
        #     "title":"问题",
        #     "is_checkbox":false,//是否多选
        #     'items':['选项1','选项2'] //问题选项
        # }
        question = data.get('question', {})
        question_obj = Question()
        question_obj.title = question.get('title', '')
        question_obj.is_checkbox = question.get('is_checkbox', False)
        question_obj.questionnaire = questionnaire
        question_obj.save()
        # 创建问题选项
        items = question.get('items', [])
        for item in items:
            item_obj = Item()
            item_obj.question = question_obj
            item_obj.content = item
            item_obj.save()
        # 将问卷状态改为草稿状态
        questionnaire.state = 0
        questionnaire.save()
        return json_response({
            'id': question_obj.id
        })
    @customer_required
    def post(self, request, *args, **kwargs):
        """
        # 更新问题
        {
            "question_id":1,//问卷id
            "title":"问题" ,//问题标题
            "is_checkbox":false,//是否为多选
            "items":["选项1",...]//问题选项
        }
        """
        user = request.user
        data = request.POST
        customer = user.customer
        question_id = data.get('question_id', 0)
        # 到问题,并且问题所在的问卷是属于当前客户,并且该问卷状态不是已发布状态
        question_exist = Question.objects.filter(
            id=question_id, questionnaire__customer=customer, questionnaire__state__in=[0, 1, 2, 3])
        if question_exist:
            question = question_exist[0]
        else:
            return params_error({
                "id": "找不到该问题,或者该问题所在问卷已发布"
            })
        # 取出该问题所在的问卷
        questionnaire = question.questionnaire
        # 更新问题
        question.title = data.get('title', '')
        question.is_checkbox = data.get('is_checkbox', False)
        question.save()
        # 删除以保存的选项
        question.item_set.all().delete()
        # 新增选项
        items = data.get('items', [])
        for item in items:
            item_obj = Item()
            item_obj.question = question
            item_obj.content = item
            item_obj.save()
        # 更新问卷状态
        questionnaire.state = 0
        questionnaire.save()
        return json_response({
            'msg': "更新成功"
        })
    @customer_required
    def delete(self, request, *args, **kwargs):
        user = request.user
        data = request.DELETE
        questionnaire_id = data.get('questionnaire_id', 0)
        question_ids = data.get('question_ids', [])
        customer = user.customer
        questionnaire_exist = Questionnaire.objects.filter(
            id=questionnaire_id, customer=customer, state__in=[0, 1, 2, 3])
        if questionnaire_exist:
            questionnaire = questionnaire_exist[0]
        else:
            return params_error({
                "questionnaire_id": "问卷不存在,或者该问卷已发布"
            })
        # 找出将要被删除的问题
        question_to_delete = Question.objects.filter(
            id__in=question_ids, questionnaire=questionnaire)
        question_deleted = [obj.id for obj in question_to_delete]
        # 删除问题
        question_to_delete.delete()
        # 更新问卷状态
        questionnaire.state = 0
        questionnaire.save()
        return json_response({
            "deleted_ids": question_deleted
        })


class CustomerQuestionnaireState(Rest):
    @customer_required
    def put(self, request, *args, **kwargs):
        user = request.user
        customer = user.customer
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id', 0)
        questionnaire_exist = Questionnaire.objects.filter(
            id=questionnaire_id, customer=customer, state=3)
        if questionnaire_exist:
            questionnaire = questionnaire_exist[0]
        else:
            return params_error({
                "questionnaire_id": "问卷不存在,或者该问卷审核未通过"
            })
        questionnaire.state = 4
        questionnaire.save()
        return json_response({
            'msg': '发布成功'
        })
