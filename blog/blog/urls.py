"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


# from django.http import HttpResponse


# # 1,导入系统的logging
# import logging
# # 2.场景(获取)日志器
# logger = logging.getLogger('django')
#
#
# def log(request):
#     # 3.使用日志器记录信息
#     logger.info('info')
#     return HttpResponse('test')



urlpatterns = [
    path('admin/', admin.site.urls),
    # include 的参数首先设置一个元组,urlcon_module,app_name
    # url_module, 设置子应用路由
    # app_name 子应用名字
    # namespace 命名空间
    path('', include(('users.urls', 'users'), namespace='users')),
    path('', include(('home.urls', 'home'), namespace='home')),
    # django的 ckedit
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # 设置ico网站图标
    path("favicon.ico", RedirectView.as_view(url='static/favicon.ico')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
