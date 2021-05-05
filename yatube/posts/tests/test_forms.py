import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

from ..models import Comment

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='GulyaevEO')
        cls.post = Post.objects.create(
            text='Самый длинный тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': TaskCreateFormTests.group.id,
            'text': 'Самый длинный тестовый пост 2',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Самый длинный тестовый пост 2',
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """При редактировании поста через форму на
        странице /<username>/<post_id>/edit/
        изменяется соответствующая запись в базе данных"""
        posts_count = Post.objects.count()
        small_gif2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif2,
            content_type='image/gif'
        )
        form_data = {
            'group': TaskCreateFormTests.group.id,
            'text': 'Самый длинный тестовый пост 3',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': TaskCreateFormTests.user,
                            'post_id': TaskCreateFormTests.post.id, }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('post_view',
                                     kwargs={
                                         'username': TaskCreateFormTests.user,
                                         'post_id': self.post.id, }))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Самый длинный тестовый пост 3',
                image='posts/small2.gif'
            ).exists()
        )

    def test_authorized_comment(self):
        """Проверка, что только неавторизованный
         пользователь  не может комментировать"""
        form_data = {
            'post': TaskCreateFormTests.post.pk,
            'text': 'Самый длинный тестовый пост 3',
            'author': TaskCreateFormTests.user,
        }
        address = (f'/{TaskCreateFormTests.user}/'
                   f'{TaskCreateFormTests.post.pk}/comment/')
        response = self.guest_client.post(
            reverse('add_comment', kwargs={
                'username': TaskCreateFormTests.user,
                'post_id': TaskCreateFormTests.post.pk,
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next={address}')
        self.assertEqual(len(Comment.objects.all()), 0)
        self.authorized_client.post(
            reverse('add_comment', kwargs={
                'username': TaskCreateFormTests.user,
                'post_id': TaskCreateFormTests.post.pk,
            }),
            data=form_data,
            follow=True
        )
        self.assertEqual(len(Comment.objects.all()), 1)
