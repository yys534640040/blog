import logging
import random
# 注册
import string
import time

from django.contrib import auth
from django.contrib.auth import logout
# 登录
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import JsonResponse
# 图形验证
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from users.models import User
# 短信验证
from .forms import LoginForm, RegisterForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm

# 写博客


logger = logging.getLogger("django")
# Create your views here.


class RegisterView(View):
    def get(self, request):
        reg_form = RegisterForm
        context = {
            'reg_form': reg_form
        }
        return render(request, 'register.html', context)

    def post(self, request):
        if request.method == 'POST':
            # 1.接收记住登录参数

            reg_form = RegisterForm(request.POST, request=request)
            if reg_form.is_valid():
                mobile = reg_form.cleaned_data["mobile"]
                email = reg_form.cleaned_data["email"]
                password = reg_form.cleaned_data['password']
                # 创建用户
                # print(mobile, email, password)
                user = User.objects.create_user(username=mobile, mobile=mobile, email=email, password=password)
                user.save()
                # 清除session
                del request.session['register_code']
                # # 登录用户
                user = auth.authenticate(mobile=mobile, password=password)
                auth.login(request, user)
                response = redirect(reverse('home:index'))

                return response
        else:
            reg_form = RegisterForm()
            pass
        context = {
            'reg_form': reg_form
        }
        return render(request, 'register.html', context)


class LoginView(View):
    def get(self, request):

        login_form = LoginForm()
        context = {
            'login_form': login_form
        }
        return render(request, 'login.html', context)

    def post(self, request):

        if request.method == 'POST':
            # 1.接收记住登录参数
            remember = request.POST.get('remember')

            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = login_form.cleaned_data['user']
                auth.login(request, user)
                # 根据next参数进行页面跳转,有from跳转到nextpage,没有则跳转首页
                response = redirect(request.GET.get('from', reverse('home:index')))
                # 设置状态保持的周期
                if remember != 'on':
                    # 没有记住用户：浏览器会话结束就过期
                    request.session.set_expiry(0)
                    # 设置cookie
                    response.set_cookie('is_login', True)
                    response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
                else:
                    # 记住用户：None表示两周后过期
                    request.session.set_expiry(None)
                    # 设置cookie
                    response.set_cookie('is_login', True, max_age=14 * 24 * 3600)
                    response.set_cookie('username', user.username, max_age=30 * 24 * 3600)

                return response
        else:
            login_form = LoginForm()
            pass
        context = {
            'login_form': login_form
        }
        return render(request, 'login.html', context)


class LogoutView(View):

    def get(self, request):
        print("退出登录")
        # 清理session
        logout(request)
        # 退出登录，
        # 方法一:通用跳转本页,否则找不到返回首页
        path = request.META.get('HTTP_REFERER', reverse('home:index'))
        response = redirect(path)
        # 方法二重定向首页
        # response = redirect(reverse('home:index'))
        # 退出登录时清除cookie中的登录状态
        response.delete_cookie('is_login')
        return response


# LoginRequiredMixin如果用户没有登录,则默认的跳转
# 默认跳转是account/login/?next = XXX
class UserCenterView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc': user.user_desc
        }
        return render(request, 'center.html', context=context)

    def post(self, request):
        # 接收数据
        user = request.user
        avatar = request.FILES.get('avatar')
        username = request.POST.get('username', user.username)
        user_desc = request.POST.get('desc', user.user_desc)

        # 修改数据库数据
        try:
            user.username = username
            user.user_desc = user_desc
            if avatar:
                user.avatar = avatar
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('更新失败，请稍后再试')

        # 返回响应，刷新页面
        response = redirect(reverse('users:center'))
        # 更新cookie信息
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
        return response


# LoginRequiredMixin 登录用户才可以写博客


def login_for_model(request):
    """弹窗登录"""
    from django.contrib import auth
    login_form = LoginForm(request.POST)
    # print(login_form)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home:index'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            username, created = User.objects.get_or_create(mobile=request.user)
            # print(username, created)

            username.nickname = nickname_new
            username.save()
            redirect_to = request.GET.get('from', reverse('home:index'))
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {
        'page_title': '修改昵称',
        'form_title': '修改昵称',
        'submit_text': '修改',
        'form': form,
        'return_back_url': redirect_to
    }
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home:index'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {
        'page_title': '绑定邮箱',
        'form_title': '绑定邮箱',
        'submit_text': '绑定',
        'form': form,
        'return_back_url': redirect_to
    }

    return render(request, 'bind_email.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')

    data = {}
    if email != '':
        # 生成验证码
        # 发送邮件
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now

        send_mail(
            '绑定邮箱',
            '验证码: %s,温馨提示:区分大小写!' % code,
            '534640040@qq.com',  # 发送者邮箱
            [email],  # 收件人的邮箱
            fail_silently=False,
        )
        data['status'] = 'SUCCESS'

    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def change_password(request):
    # 和修改昵称类似,redirect_to跳转到登录页面
    redirect_to = reverse('users:login')

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            # 退出登录
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()
    context = {
        'page_title': '修改密码',
        'form_title': '修改密码',
        'submit_text': '修改',
        'form': form,
        'return_back_url': redirect_to
    }

    return render(request, 'form.html', context)


def forgot_password(request):
    redirect_to = reverse('users:login')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data["email"]
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()
    context = {
        'page_title': '重置密码',
        'form_title': '重置密码',
        'submit_text': '重置',
        'form': form,
        'return_back_url': redirect_to
    }

    return render(request, 'forgot_password.html', context)
