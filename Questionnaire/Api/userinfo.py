import math
from datetime import datetime

from django.utils import timezone

from Api.utils import *
from Api.resources import Rest
from Api.decorators import *
from Question.models import *


class UserInfoQuestionnaire(Rest):
    @userinfo_required
    def get(self, request, *args, **kwargs):
        data = request.GET
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 10))
        start_id = int(data.get('start_id', 1))
        with_detail = data.get('with_detail', False)

        questionnaire = Questionnaire.objects.filter(
            id__gte=start_id, state=4)

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
            questionnaire_dict['customer'] = {
                "id": obj.customer.id,
                "company_name": obj.customer.company_name
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


class UserInfoJoinQuestionnaire(Rest):
    @userinfo_required
    def get(self, request, *args, **kwargs):
        data=request.GET 
        page=int(data.get('page',1))
        limit=int(data.get('limit',10))
        start_id=int(data.get('start_id',1))
        join_objs=JoinQuestionnaire.objects.filter(userinfo=request.user.userinfo)
        count=join_objs.count()
        pages=math.ceil(count/limit) or 1
        if page>pages:
            page=pages
        # 取出当前页面数据
        start=(page-1)*limit
        end=page*limit
        objs=join_objs[start:end]
        # 构建结果字典
        result=dict()
        result['objs']=[]
        for obj in objs:
            join_dict=dict()
            join_dict['id']=obj.id
            join_dict['create_date']=datetime.strftime(obj.create_date,'%Y-%m-%d')
            join_dict['questionnaire']={
                "id":obj.questionnaire.id,
                "title":obj.questionnaire.title
            }
            join_dict['customer']={
                "id":obj.questionnaire.customer.id,
                "company_name":obj.questionnaire.customer.company_name
            }

            result['objs'].append(join_dict)
        
        return json_response(result)

    @userinfo_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id', 0)
        # 判断问卷是否是已发布,是否未过期,是否还有剩余数量
        # 通常情况与当前时间进行比较,应该使用django.utils.timezone.now而不是datetime.now
        questionnaire_exist=Questionnaire.objects.filter(id=questionnaire_id,state=4,expire_date__gte=timezone.now(),left__gte=1)
        if questionnaire_exist:
            questionnaire=questionnaire_exist[0]
        else:
            return params_error({
                "questionnaire_id":"问卷不存或者该问卷不可参与"
            })
        # 判断当前用户是否参与过该问卷
        if JoinQuestionnaire.objects.filter(userinfo=request.user.userinfo,questionnaire=questionnaire):
            return params_error({
                "msg":"已经参与过该问卷"
            })
        
        # 添加参与信息
        join=JoinQuestionnaire()
        join.userinfo=request.user.userinfo
        join.questionnaire=questionnaire
        join.create_date=datetime.now()
        join.is_done=False
        join.save()
        # 把问卷剩余数量减1
        questionnaire.left=questionnaire.left-1
        questionnaire.save()
        return json_response({
            "id":join.id
        })

    @userinfo_required 
    def delete(self, request, *args, **kwargs):
        data=request.DELETE 
        userinfo=request.user.userinfo 
        join_ids=data.get('ids',[])

        join_to_delete=JoinQuestionnaire.objects.filter(id__in=join_ids,userinfo=userinfo)

        deleted_ids=[]

        for join in join_to_delete:
            # 更新问卷剩余数量
            questionnaire=join.questionnaire
            questionnaire.left=questionnaire.left+1
            questionnaire.save()
            # 将要删除对的参与信息id取出来
            deleted_ids.append(join.id)
        
        # 删除参与信息
        join_to_delete.delete()

        return json_response({
            'deleted_ids':deleted_ids
        })

class UserInfoAnswerQuestionnaire(Rest):
    @userinfo_required
    def get(self,request,*args,**kwargs):
        data=request.GET
        userinfo=request.user.userinfo 
        questionnaire_id=data.get('questionnaire_id',0)
        questionnaire=Questionnaire.objects.get(id=questionnaire_id)
        # 判断是否参与过该问卷
        has_joined=JoinQuestionnaire.objects.filter(userinfo=userinfo,questionnaire=questionnaire)
        if not has_joined:
            return params_error({
                'questionnaire_id':"未参与该问卷"
            })
        # 构建问卷答案信息
        result=dict()
        # 取出问卷信息
        result['questionnaire']={
            'id':questionnaire.id,
            'title':questionnaire.title
        }
        # 取出客户信息
        result['customer']={
            'id':questionnaire.customer.id,
            'company_name':questionnaire.customer.company_name
        }
        # 取出问卷下问题
        result['questions']=[]
        for question in questionnaire.question_set.all():
            question_dict=dict()
            question_dict['id']=question.id
            question_dict['title']=question.title
            question_dict['is_checkbox']=question.is_checkbox
            # 找出用户所选的选项
            answers=AnswerQuestionnaire.objects.filter(userinfo=userinfo,item__question=question)
            question_dict['answer_items']=[]
            for answer in answers:
                answer_dict=dict()
                answer_dict['id']=answer.id 
                # 把所选择的选项数据取出来
                answer_dict['item']={
                    'id':answer.item.id,
                    'content':answer.item.content
                }
                question_dict['answer_items'].append(answer_dict)
            # 问题下所有选项取出来
            question_dict['items']=[]
            for item in question.item_set.all():
                item_dict=dict()
                item_dict['id']=item.id
                item_dict['content']=item.content
                question_dict['items'].append(item_dict)

            result['questions'].append(question_dict)
        return json_response(result)

    @userinfo_required
    def put(self,request,*args,**kwargs):
        data=request.PUT 
        user=request.user
        userinfo=user.userinfo
        # 找出客户端选择的选项
        item_id=data.get('item_id',0)
        item=Item.objects.get(id=item_id)
        # 判断问卷是否是已发布状态
        if item.question.questionnaire.state!=4:
            return params_error({
                "item_id":"该问卷为发布"
            })
        # 判断是否参与了该问卷
        if not JoinQuestionnaire.objects.filter(questionnaire=item.question.questionnaire,userinfo=userinfo,is_done=False):
            return params_error({
                "item_id":"未参与该问卷或者该问卷答案已提交完成"
            })
        # 判断题型
        question=item.question
        if question.is_checkbox:
            # 多选题
            # 判断是否选择过该选项
            item_selected=AnswerQuestionnaire.obejcts.filter(userinfo=userinfo,item=item)
            if not item_selected:
                # 如果没有选择过该选项,那么添加进来
                answer_item=AnswerQuestionnaire()
                answer_item.userinfo=userinfo
                answer_item.item=item
                answer_item.save()
                return json_response({
                    'id':item.id
                })
            return params_error({
                'item_id':'已经选择过该选项'
            })
        else:
            # 单选题
            # 判断选择过该选项
            item_selected=AnswerQuestionnaire.objects.filter(userinfo=userinfo,item=item)
            # 如果回答过该问题,就把之前的选项删除
            if item_selected:
                item_selected.delete()
            # 添加选项
            answer_item=AnswerQuestionnaire()
            answer_item.userinfo=userinfo
            answer_item.item=item
            answer_item.save()
            return json_response({
                'id':answer_item.id
            })
    
    @userinfo_required
    def delete(self,request,*args,**kwargs):
        userinfo=request.user.userinfo
        data=request.DELETE
        item_id=data.get('item_id',0)
        # 检查该用户是否选择过改选,如果选择过就删除,否则不管
        item_selected=AnswerQuestionnaire.objects.filter(item=Item.objects.get(id=item_id),userinfo=userinfo)
        # 如果选择过就删除
        if item_selected:
            item_selected.delete()
            return json_response({
                "msg":"删除选项成功"
            })
        else:
            return params_error({
                "msg":"没有选择过该选项"
            })