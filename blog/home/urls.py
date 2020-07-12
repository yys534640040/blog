from django.urls import path
from home.views import IndexView, DetailView, UpdateArticleView, SearchArticleView,  WriteBlogView
from . import views

urlpatterns = [
    # 首页
    path('', IndexView.as_view(), name='index'),
    #  详情视图路由
    path('detail/', DetailView.as_view(), name='detail'),
    #  修改文章
    path('updateblog/', UpdateArticleView.as_view(), name='updateblog'),
    #  查找文章
    path('search/', SearchArticleView.as_view(), name='search'),
    # 点赞
    path('like_change', views.like_change, name='like_change'),

    # 写博客
    path('writeblog/', WriteBlogView.as_view(), name='writeblog'),


]
