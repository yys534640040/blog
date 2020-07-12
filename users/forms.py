from django import forms
from django.contrib import auth
from django.contrib.auth import get_user_model  # 要加上这句话不然会报错（1）

from home.models import Article
from home.models import Comment

User = get_user_model()


class LoginForm(forms.Form):
    # 用邮箱或手机登录
    mobile_or_email = forms.CharField(label="用户名", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '请输入手机号或邮箱'}))
    password = forms.CharField(label="密码", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入密码'}))

    def clean(self):
        """login登录验证"""
        mobile_or_email = self.cleaned_data['mobile_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate(mobile=mobile_or_email, password=password)

        if user is None:
            # 用邮箱登录
            if User.objects.filter(email=mobile_or_email).exists():
                mobile = User.objects.get(email=mobile_or_email).mobile
                user = auth.authenticate(username=mobile, password=password)
                if user:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError("用户名或密码不正确")
        else:
            self.cleaned_data['user'] = user
        # 返回user给views
        return self.cleaned_data


class RegisterForm(forms.Form):
    mobile = forms.CharField(label="用户名", max_length=11, min_length=3, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '请输入手机号'}))
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))

    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )

    password = forms.CharField(label="密码", min_length=6, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password_again = forms.CharField(label="再输入一次密码", min_length=6, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '再输入一次密码'}))

    # request是获取session
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断验证码register_code对应js里面的send_for
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')

        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')

        return self.cleaned_data

    def clean_username(self):
        mobile = self.cleaned_data['mobile']
        if User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('用户名已存在')
        return mobile

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError("两次密码不一致")
        return password

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


# 修改用户昵称
class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(
        label="新的昵称",
        required=False,
        max_length=20,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'})
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError("新的昵称不能为空")
        return nickname_new


class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label="邮箱",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'})
    )

    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )

    # request是获取session
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断用户是否已绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定邮箱')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')

        return self.cleaned_data

    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="密码", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入旧的密码'}))
    new_password = forms.CharField(label="密码", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))
    new_password_again = forms.CharField(label="密码", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请再次输入的密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断两次新密码是否一致
        new_password = self.cleaned_data['new_password']
        new_password_again = self.cleaned_data['new_password_again']
        if new_password != new_password_again or new_password == '':
            return forms.ValidationError("两次密码不一致")
        return self.cleaned_data

    def clean_old_password(self):
        #  判断旧密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("旧密码不正确")
        return old_password


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="邮箱",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入忘记密码的邮箱'})
    )

    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )
    new_password = forms.CharField(label="新的密码", min_length=6, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if not User.objects.filter(email=email).exists():
            return forms.ValidationError("你输入的邮箱不存在")
        return email

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean_verification_code(self):

        # 判断验证码是否为空
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')

        # 判断验证码register_code对应js里面的send_for
        code = self.request.session.get('forgot_password_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')

        return verification_code

# CKeditor文章
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['content']


# CKeditor评论
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
