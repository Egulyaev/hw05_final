from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()
MAX_POST_PER_PAGE = 10


def index(request):
    """Главная страница"""
    post_list = Post.objects.all()
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
    post_list = Post.objects.filter(author__following__user=request.user)
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
    if follower != following:
        Follow.objects.get_or_create(user=follower, author=following)
    return redirect(
        'profile',
        username=username
    )


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect(
        'profile',
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
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'page': page,
            'author': author,
            'username': username,
            'following': following,
        }
    )


def post_view(request, username, post_id):
    """Страница поста с комментариями"""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
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
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == "GET" or not form.is_valid():
        return render(
            request,
            'posts/new.html',
            {'form': form, 'is_edit': True, 'post': post}
        )
    form.save()
    return redirect(
        post_view,
        username=username,
        post_id=post.pk,
    )


@login_required
def add_comment(request, username, post_id):
    """Обработка и вывод комментариев"""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
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
