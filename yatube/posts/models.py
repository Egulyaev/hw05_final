from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Наименование группы"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Поле формирования Slug для Group"
    )
    description = models.TextField(verbose_name="Описание группы")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Группы"
        verbose_name = "Группа"


class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор поста")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name="posts",
                              verbose_name="Группа поста")
    image = models.ImageField(upload_to="posts/", blank=True, null=True,
                              verbose_name="Изображение")

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = "Посты"
        verbose_name = "Пост"


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="comments",
                             verbose_name="Комментируемый пост")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор комментария")
    text = models.TextField(verbose_name="Текст комментария")
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name="Дата комментария")

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name_plural = "Комментарии"
        verbose_name = "Коментарий"


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name="Подписчик")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following",
                               verbose_name="Автор")

    def __str__(self):
        return (f'User: {self.user.username[:15]},'
                f' Author: {self.author.username[:15]}')

        class Meta:
            verbose_name_plural = "Подписчики"
            verbose_name = "Подписчик"
