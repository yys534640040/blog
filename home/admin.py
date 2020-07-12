from django.contrib import admin
from home.models import ArticleCategory, Article, Comment

# Register your models here.
# 注册模型

admin.site.register(ArticleCategory)


class ArticleAdmin(admin.ModelAdmin):

    list_display = ('title', 'id',  'category', 'created', 'updated')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
