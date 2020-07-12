from django import template

from home.models import Comment
from ..forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount, LikeRecord

# 自定义模板标签
# 注册变成模板标签
register = template.Library()


@register.simple_tag
def get_comment_count(obj):
    # obj文章名字
    total_count = Comment.objects.filter(article=obj).order_by('-created').count()
    return total_count


@register.simple_tag
def get_comment_form(obj):
    # 获取该类对应表名（字符串类型）
    # print(obj._meta.get_field('content').verbose_name)
    
    form = CommentForm(
        initial={'content_type': obj._meta.model_name, 'object_id': obj.id, 'reply_comment_id': '0'})  # 评论使用富文本设定
    return form


@register.simple_tag
def get_like_count(obj):
    # 获取点赞总数
    content_type = ContentType.objects.get_for_model(obj)
    like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.id)
    return like_count.liked_num


@register.simple_tag(takes_context=True)
def get_like_status(context, obj):
    # 获取点赞状态
    content_type = ContentType.objects.get_for_model(obj)
    user = context['user']
    if not user.is_authenticated:
        # 用户没有登录赞都是原来颜色,用户登录的话,且是此用户点的赞,如果红色就显示红色
        return ''
    if LikeRecord.objects.filter(content_type=content_type, object_id=obj.id, user=user).exists():
        return 'active'
    else:
        return ''


@register.simple_tag
def get_content_type(obj):
    content_type = obj._meta.model_name

    return content_type
