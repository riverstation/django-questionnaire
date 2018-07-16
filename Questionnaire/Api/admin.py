import math
from datetime import datetime

from Api.utils import *
from Api.resources import Rest
from Question.models import *
from Api.decorators import *

class AdminQuestionnaire(Rest):
    @admin_required
    def get(self,request,*args,**kwargs):
        user = request.user
        # customer = user.customer
        data = request.GET
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 10))
        start_id = int(data.get('start_id', 1))
        with_detail = data.get('with_detail', False)

        questionnaire = Questionnaire.objects.filter(
            id__gte=start_id, state=1)

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

            # 把客户信息取出来
            questionnaire_dict['customer']={
                "id":obj.customer.id,
                "company_name":obj.customer.company_name
            }

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

            result['objs'].append(questionnaire_dict)
        return json_response(result)

class QuestionnaireCommentResource(Rest):
    @admin_required
    def put(self,request,*args,**kwargs):
        user=request.user
        data=request.PUT 
        admin=user.admin
        questionnaire_id=data.get('questionnaire_id',0)
        is_agree=data.get('is_agree',False)
        comment=data.get('comment','')
        # 找出问卷
        questionnaire_exist=Questionnaire.objects.filter(id=questionnaire_id,state=1)
        if questionnaire_exist:
            questionnaire=questionnaire_exist[0]
        else:
            return params_error({
                "questionnaire_id":"问卷不存在,或者该问卷非待审核状态"
            })
        if is_agree:
            # 如果同意,将问卷状态保存为审核通过
            questionnaire.state=3
            questionnaire.save()
        else:
            # 如果不同意,首先判断是否提交了批注信息,保存批注信息,将问卷状态修改为审核未通过
            if comment:
                comment_obj=QuestionnaireComment()
                comment_obj.questionnaire=questionnaire
                comment_obj.comment=comment
                comment_obj.admin=admin
                comment_obj.save()
            else:
                return params_error({
                    'comment':"必须提供批注信息"
                })
            questionnaire.state=2
            questionnaire.save()
        return json_response({
                "msg":"提交成功"
            })
            

            

