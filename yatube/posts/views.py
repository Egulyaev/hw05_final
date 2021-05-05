from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow

User = get_user_model()
MAX_POST_PER_PAGE = 10


def index(request):
    """Главная страница"""
    user = get_object_or_404(User, username=request.user)
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, MAX_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page': page}
    )


@login_required
def follow_index(request):
        """Страница подписчика с постами"""
        user = get_object_or_404(User, username=request.user)
        author_get = Follow.objects.filter(user=user)
        author_list = [author.author for author in author_get ]
        post_list = Post.objects.filter(author__username__in=author_list)
        paginator = Paginator(post_list, MAX_POST_PER_PAGE)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        return render(
            request,
            'posts/follow.html',
            {'page': page}
        )


@login_required
def profile_follow(request, username):
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, username=username)
    if follower == following:
        return redirect(
            profile,
            username=username
        )
    follow = Follow()
    follow.user = follower
    follow.author = following
    follow.save()
    return redirect(
        profile,
        username=username
    )


@login_required
def profile_unfollow(request, username):
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, username=username)
    instance = Follow.objects.filter(user=follower, author=following)
    instance.delete()
    return redirect(
        profile,
        username=username,
    )


def group_posts(request, slug):
    """Страница группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, MAX_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/group.html",
        {"group": group, "page": page}
    )


@login_required
def new_post(request):
    """Страница создания нового поста"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "GET" or not form.is_valid():
        return render(
            request,
            "posts/new.html",
            {"form": form, "is_edit": False}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect("index")


def profile(request, username):
    """Страница автора (профайл)"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, MAX_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follows = len(Follow.objects.filter(user=author))
    followers = len(Follow.objects.filter(author=author))
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=follower, author=following):
        return render(
            request,
            'posts/profile.html',
            {'page': page, 'author': author, 'username': username, 'followers': followers, 'follows':  follows, 'following': True}
        )
    return render(
        request,
        'posts/profile.html',
        {'page': page, 'author': author, 'username': username, 'followers': followers, 'following': False, 'follows': follows}
    )



def post_view(request, username, post_id):
    """Страница поста с комментариями"""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post_id)
    return render(
        request,
        'posts/post.html',
        {'post': post, 'author': author, 'form': form, 'comments': comments}
    )


@login_required
def post_edit(request, username, post_id):
    """Страница редактирования поста"""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect(
            post_view,
            username=username,
            post_id=post.pk,
        )
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "GET" or not form.is_valid():
        return render(
            request,
            'posts/new.html',
            {'form': form, 'is_edit': True}
        )
    post.save()
    return redirect(
        post_view,
        username=username,
        post_id=post.pk,
    )


@login_required
def add_comment(request, username, post_id):
    """Обработка и вывод комментариев"""
    post = get_object_or_404(Post, pk=post_id)
    comment_author = get_object_or_404(User, username=request.user)
    form = CommentForm(request.POST or None)
    if request.method == "GET" or not form.is_valid():
        return render(
            request,
            'posts/post.html',
            {'form': form}
        )
    comment = form.save(commit=False)
    comment.author = comment_author
    comment.post = post
    comment.save()
    return redirect(
        post_view,
        username=username,
        post_id=post.pk,
    )


def page_not_found(request, exception):
    """Страница не найдена"""
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    """Ошибка сервера"""
    return render(request, "misc/500.html", status=500)
