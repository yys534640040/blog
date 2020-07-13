import threading

# from ckeditor.fields import RichTextField # 不支持上传文件的富文本字段
from ckeditor_uploader.fields import RichTextUploadingField  # 支持上传文件的富文本字段
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from users.models import User


# Create your models here.
# 多线发邮件
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject,
                  self.text,
                  settings.EMAIL_HOST_USER,
                  [self.email],
                  fail_silently=self.fail_silently,
                  html_message=self.text

                  )


class ArticleCategory(models.Model):
    """
    文章分类
    """
    # 分类标题
    title = models.CharField(max_length=100, blank=True)
    # 分类的创建时间
    created = models.DateTimeField(default=timezone.now)

    # admin站点显示, 调试查看对象方便

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tb_category'  # 修改表明
        verbose_name = '类别管理'  # admin站点显示
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    作者
    标题图
    标题
    分类
    标签
    摘要信息
    文章正文
    浏览量
    评论量
    文章的创建时间
    文章修改时间
    """
    # 作者
    # 参数on_delete就是当user表中数据删除后,文章信息也同步删除
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 标题图和头像一个文件夹,都是年月日形式
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 标题
    title = models.CharField(max_length=200, blank=True)
    # 分类
    category = models.ForeignKey(ArticleCategory, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='article')
    # 标签
    tags = models.CharField(max_length=20, blank=True)
    # 摘要信息
    sumary = models.CharField(max_length=200, null=False, blank=False)
    # 文章正文
    # content = models.TextField()

    content = RichTextUploadingField()
    # 浏览量
    total_views = models.PositiveIntegerField(default=0)
    # # 评论量
    # comments_count = models.PositiveIntegerField(default=0)
    # 文章的创建时间
    created = models.DateTimeField(auto_now_add=True)

    # 文章修改时间
    updated = models.DateTimeField(auto_now=True)

    def get_url(self, request):
        """获得网站url绝对路径"""
        return request.build_absolute_uri()

    def get_email(self):
        return self.author.email

    class Meta:
        db_table = 'tb_article'
        ordering = ('-created',)  # 排序
        verbose_name = '文章管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    评论内容
    评论文章
    评论用户
    评论时间
    用户回复
    """
    # 评论内容
    # content = models.TextField()

    content = RichTextUploadingField(config_name="selfmake")  # 自己定义的CKeditor

    # 评论文章  # on_delete=models.CASCADE删除Article文章后可以把评论删除了
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    # 评论用户,related_name防止冲突,名字自定义的
    user = models.ForeignKey('users.User', related_name="comments", on_delete=models.SET_NULL, null=True)
    # 评论时间
    created = models.DateTimeField(auto_now_add=True)

    # 记录每一条回复从哪里开始的,related_name防止冲突,名字自定义的
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.DO_NOTHING)
    # 上一级
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.DO_NOTHING)
    # 回复谁的
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.DO_NOTHING)

    def sen_email(self, request):
        if self.parent is None:
            # 评论
            subject = "有人评论我的文章"
            email = self.article.get_email()

        else:
            # 回复
            subject = "有人回复你的评论"
            email = self.reply_to.email
        print(self.article.get_url(request))
        if email:
            context = {
                'comment_text': self.content,
                "url": self.article.get_url(request)
            }
            # 发送给html模板
            text = render_to_string('send_email.html', context)
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.article.title

    class Meta:
        db_table = 'tb_comment'
        verbose_name = '评论管理'
        verbose_name_plural = verbose_name
        ordering = ['created']  # 让回复内容正序,从上往下


class LikeCount(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    liked_num = models.IntegerField(default=0)


class LikeRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_time = models.DateTimeField(auto_now_add=True)
