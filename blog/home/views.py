import random
import re

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage
from django.db.models import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.http.response import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect, reverse
from django.views import View

from home.forms import CommentForm
from home.models import ArticleCategory, Article
from home.models import Comment
from users.forms import ArticleForm
from .models import LikeCount, LikeRecord


# import pymysql
# Create your views here.
# def write_log(text):
#     db = pymysql.connect(host='localhost', port=3306, user='root', password='123456', database='log',
#                          charset='utf8mb4')
#     cursor = db.cursor()
#     ins = 'insert into print(content) values (%s)'

#     cursor.execute(ins, text)
#     db.commit()
#     cursor.close()
#     db.close()


def checkMobile(request):
    # 判断网站来自mobile还是pc
    userAgent = request.headers['User-Agent']

    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(userAgent) != None:
        return True
    user_agent = userAgent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False


class IndexView(View):
    def get(self, request):
        """
        1.获取所有分类信息
        2.接收用户点击分类id
        3.一句分类id进行分类查询
        4.获取分页参数
        5.根据分类信息查询文章数据
        6.创建分页器
        7.进行分页处理
        8.组织数据传递给模板
        :param request:
        :return:
        """
        # print(request.user.username)
        # 判断否是手机
        is_mobile = checkMobile(request)
        """提供首页广告界面"""
        # ?cat_id=xxx&page_num=xxx&page_size=xxx
        cat_id = request.GET.get('cat_id', 1)
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)

        # #判断分类id
        # try:
        category = ArticleCategory.objects.get(id=cat_id)
        # except ArticleCategory.DoesNotExist:
        #     return HttpResponseNotFound('没有此分类')

        # 获取博客分类信息
        categories = ArticleCategory.objects.all()
        # 下面是随机获取图片,文字进行图片轮播
        all_article = Article.objects.all()
        # print(all_article)
        # 获取id列表
        ids = Article.objects.values_list('id')
        count = len(ids)  # 获取总体数
        # print(count)
        s = []

        while len(s) < 3:
            x = random.randint(0, count - 1)
            if x not in s:
                s.append(x)
        # print(s)
        num1, num2, num3 = ids[s[0]][0], ids[s[1]][0], ids[s[2]][0]

        # 分页数据
        articles = Article.objects.filter(
            category=category
        )

        # 创建分页器：每页N条记录
        paginator = Paginator(articles, page_size)
        # 获取每页商品数据
        try:
            page_articles = paginator.page(page_num)

        except EmptyPage:
            # 如果没有分页数据，默认给用户404
            return HttpResponseNotFound('empty page')
        # 获取列表页总页数
        total_page = paginator.num_pages

        # 查询浏览器前10的文章数据(推荐的)
        hot_articles = Article.objects.order_by('-total_views')[:9]
        context = {
            'categories': categories,
            'category': category,
            'articles': page_articles,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
            'all_article': all_article,
            'num1': int(num1),
            'num2': int(num2),
            'num3': int(num3),
            'is_mobile': is_mobile,
            'hot_articles': hot_articles
        }

        return render(request, 'index.html', context=context)


class DetailView(View):
    def get(self, request):
        """
        1.接收文章id信息
        2.根据文章id进行文章数据的查询
        3.查询分类信息
        4.获取分页请求参数
        5.根据文章信息查询评论数据
        6.创建分页器
        7.进行分页处理
        8.组织模板数据
        :param request:
        :return:
        """
        is_mobile = checkMobile(request)

        # print(is_mobile)
        # write_log(is_mobile)
        # 1.接收文章id信息
        id = request.GET.get('id')
        # 2.根据文章id进行文章数据的查询
        try:
            article = Article.objects.get(id=id)

            previous_blog = Article.objects.filter(created__gt=article.created).last()
            next_blog = Article.objects.filter(created__lt=article.created).first()
            # print(previous_blog, next_blog)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:
            # 让浏览量+1(如果没有访问cookie就+1,如果读到就不进)
            if not request.COOKIES.get("blog_%s_readed" % id):
                article.total_views += 1
                article.save()

        # 3.查询分类信息
        categories = ArticleCategory.objects.all()
        # 4.获取分页请求参数
        page_size = request.GET.get('page_size', 10)
        page_num = request.GET.get('page_num', 1)
        # 5.根据文章信息查询评论数据, parent=None,如果不加回复后或多于一楼
        comments = Comment.objects.filter(article=article, parent=None).order_by('-created')  # 根据创建时间排序
        # print(comments)

        # 6.创建分页器
        paginator = Paginator(comments, page_size)
        try:
            pag_commens = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty, page')
        # 总页数
        total_page = paginator.num_pages
        # 7.进行分页处理
        # 8.组织模板数据

        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'comments': pag_commens,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
            'is_mobile': is_mobile,
            'previous_blog': previous_blog,
            'next_blog': next_blog,
        }
        response = render(request, 'detail.html', context=context)
        response.set_cookie('blog_%s_readed' % id, 'ture')  # 为了浏览量设置
        return response

    def post(self, request):
        comment_form = CommentForm(request.POST, user=request.user)

        data = {}
        if comment_form.is_valid():
            # 检查通过，保存数据

            comment = Comment()
            comment.content = comment_form.cleaned_data['content']
            comment.article = comment_form.cleaned_data['content_object']
            comment.user = comment_form.cleaned_data['user']

            # 判断是否是回复
            parent = comment_form.cleaned_data['parent']
            if parent:
                comment.root = parent.root if parent.root else parent
                comment.parent = parent
                comment.reply_to = parent.user
            comment.save()

            # 发送邮件
            comment.sen_email(request)
            # 返回评论数据.get_nickname()是users:model里面的如果有昵称返回昵称,没有就返回手机号,是评论不刷新页面出现
            data['status'] = 'SUCCESS'
            data['user'] = comment.user.get_nickname()
            data['created'] = comment.created.strftime('%Y-%m-%d %H:%M:%S')
            data['content'] = comment.content
            data['content_type'] = comment.article._meta.model_name

            # return JsonResponse(data)

            # 返回回复数据
            if parent:
                data['reply_to'] = comment.reply_to.get_nickname()
            else:
                data['reply_to'] = ''
            data['id'] = comment.id
            data['root_id'] = comment.root.id if comment.root else ''
            # print("#root_%s" % data['root_id'])

        else:
            data['status'] = 'ERROR'
            data['message'] = list(comment_form.errors.values())[0][0]
        return JsonResponse(data)


def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message

    return JsonResponse(data)


def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    # print(data)
    return JsonResponse(data)


def like_change(request):
    # print("点赞")
    # 获取数据
    user = request.user

    content_type = request.GET.get('content_type')

    object_id = request.GET.get('object_id')

    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)

    except ObjectDoesNotExist:
        return ErrorResponse(401, 'object not exist')

    # 处理数据
    if request.GET.get('is_like') == 'true':
        # 要点赞
        if not user.is_authenticated:
            return ErrorResponse(400, '没有登录,不能点赞')

        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id,
                                                                user=user)
        # print(like_record, created)
        if created:
            # 未点赞过，进行点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return ErrorResponse(402, 'you were liked')
    else:
        # 要取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数减1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(404, 'data error')
        else:
            # 没有点赞过，不能取消
            return ErrorResponse(403, 'you were not liked')


class UpdateArticleView(View):
    """可以返回到updateblog.html"""

    def get(self, request):
        # 1.接收文章id信息
        # 1.线接收用户信息
        user = request.user
        # 2.判断用户是否登录
        if user and user.is_authenticated:
            id = request.GET.get('id')
            # 2.根据文章id进行文章数据的查询
            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return render(request, '404.html')

            # print(article.content)
            categories = ArticleCategory.objects.all()
            from users.forms import ArticleForm
            comment_form = ArticleForm()  # 富文本设定

            context = {
                'article': article,
                'categories': categories,
                'comment_form': comment_form
            }
            # context可以返回到updateblog.html
            return render(request, 'updateblog.html', context=context)
        else:
            return redirect(reverse('users:login'))

    def post(self, request):
        """
        1.接收数据
        2.验证数据
        3.数据入库
        4.跳转到指定页面(暂时首页)
        :param request:
        :return:
        """

        # 1.接收数据
        id = request.GET.get('id')
        article = Article.objects.get(id=id)

        avatar = article.avatar
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags')
        sumary = request.POST.get('sumary')
        content = request.POST.get('content')
        # 2.验证数据
        # 2.1验证参数是否齐全
        if not all([avatar, title, category_id, sumary, content]):
            return HttpResponseBadRequest('参数不全')
        # 2.2 判断分类id
        # try:
        #     category = ArticleCategory.objects.get(id=category_id)
        # except ArticleCategory.DoesNotExist:
        #     return HttpResponseBadRequest('没有此分类')

        # 3.数据入库
        try:
            category = ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('没有此分类')

        try:
            # print(id, title)
            article.title = title

            article.avatar = avatar
            article.content = content
            article.tags = tags
            article.sumary = sumary
            article.category = category

            article.save()

        except Exception as e:
            print(e)
            return HttpResponseBadRequest('发布失败,请稍后再试')
        # 4.跳转到指定页面(暂时首页)

        path = reverse('home:detail') + '?id={}'.format(article.id)
        return redirect(path)


class SearchArticleView(View):
    def get(self, request):
        search_word = request.GET.get('q').strip()
        # 分词筛选:按&|~
        condition = None
        for word in search_word.strip(' '):
            if condition is None:
                condition = Q(title__icontains=word)  # __contains包含关键字,加i是忽略大小写
            else:
                condition = condition | Q(title__icontains=word)
        search_blogs = []
        if condition is not None:
            # 筛选:搜索
            search_blogs = Article.objects.filter(condition)
        # 分页

        paginator = Paginator(search_blogs, 10)
        page_num = request.GET.get('page', 1)
        page_of_blogs = paginator.get_page(page_num)

        # #判断分类id
        categories = ArticleCategory.objects.all()  # 分类显示科目分类
        context = {
            'search_word': search_word,
            'search_blogs_count': search_blogs.count,  # 博客的总数
            'search_blogs': search_blogs,
            'page_of_blogs': page_of_blogs,
            'categories': categories
        }
        return render(request, 'search.html', context=context)


class WriteBlogView(LoginRequiredMixin, View):
    def get(self, request):
        # 查询所有分类
        categories = ArticleCategory.objects.all()
        article = Article.objects.all()
        comment_form = ArticleForm()
        context = {'categories': categories,
                   'article': article,
                   'comment_form': comment_form
                   }
        print(comment_form)
        return render(request, 'write_blog.html', context=context)

    def post(self, request):
        """
        1.接收数据
        2.验证数据
        3.数据入库
        4.跳转到指定页面(暂时首页)
        :param request:
        :return:
        """

        # 1.接收数据
        avatar = request.FILES.get('avatar')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags')
        sumary = request.POST.get('sumary')
        content = request.POST.get('content')
        user = request.user
        # 2.验证数据
        # 2.1验证参数是否齐全
        if not all([avatar, title, category_id, sumary, content]):
            return HttpResponseBadRequest('参数不全')
        # 2.2 判断分类id
        try:
            category = ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('没有此分类')

        # 3.数据入库
        try:
            article = Article.objects.create(
                author=user,
                avatar=avatar,
                category=category,
                tags=tags,
                title=title,
                sumary=sumary,
                content=content
            )
        except Exception as e:
            pass
            return HttpResponseBadRequest('发布失败,请稍后再试\n' + str(e))
        # 4.跳转到新发的页面
        path = reverse('home:detail') + '?id={}'.format(article.id)

        return redirect(path)
