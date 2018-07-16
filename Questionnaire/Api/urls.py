from Api.resources import Register
from Api.common import *
from Api.customer import *
from Api.admin import *
from Api.userinfo import *

api=Register()
api.regist(RegistCode('regist_code'))
api.regist(UserResource('user'))
api.regist(Session())
api.regist(CustomerQuestionnaire('customer_questionnaire'))
api.regist(CustomerQuestionnaireState('customer_questionnaire_state'))
api.regist(CustomerQuestion('customer_question'))
api.regist(AdminQuestionnaire('admin_questionnaire'))
api.regist(QuestionnaireCommentResource('admin_questionnaire_comment'))
api.regist(UserInfoQuestionnaire('userinfo_questionnaire'))
api.regist(UserInfoJoinQuestionnaire('userinfo_join_questionnaire'))
api.regist(UserInfoAnswerQuestionnaire('userinfo_answer_questionnaire'))