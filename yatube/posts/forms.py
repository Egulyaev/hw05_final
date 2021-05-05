from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'group': _('Группа принадлежности поста'),
            'text': _('Содержание поста'),
            'image': _('Иллюстрация к посту'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': _('Текст комментария'),
        }
