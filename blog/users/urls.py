# 用于进行users子应用视图路由
from django.urls import path
from users.views import RegisterView,  LoginView, LogoutView
from users.views import UserCenterView
from . import views

urlpatterns = [
    # 都一个参数:路由
    # 注册
    path('register/', RegisterView.as_view(), name='register'),

    # 登录
    path('login/', LoginView.as_view(), name='login'),
    #  退出登录
    path('logout/', LogoutView.as_view(), name='logout'),

    # 个人中心
    path('center/', UserCenterView.as_view(), name='center'),

    # 弹窗登录
    path('login_for_model', views.login_for_model, name='login_for_model'),
    # 修改昵称
    path('change_nickname', views.change_nickname, name='change_nickname'),
    # 绑定邮箱
    path('bind_email', views.bind_email, name='bind_email'),
    # 发送验证码
    path('send_verification_code', views.send_verification_code, name='send_verification_code'),
    # 修改密码
    path('change_password', views.change_password, name='change_password'),
    # 忘记密码
    path('forgot_password', views.forgot_password, name='forgot_password'),

]
