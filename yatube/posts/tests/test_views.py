import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

TEST_CACHE_SETTING = {}
User = get_user_model()
POST_PER_PAGE = 10


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='GulyaevEO')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Самый длинный тестовый пост',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.group2 = Group.objects.create(
            title='Проверка',
            description='Проверочный текст',
            slug='proverka'
        )
        cls.user2 = User.objects.create_user(username='leo')
        cls.post2 = Post.objects.create(
            text='Пост для проверки подписок',
            author=cls.user2,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.user3 = User.objects.create_user(username='john')

        cls.all_urls = (
            (reverse('index'), 'posts/index.html'),
            (reverse(
                'group_posts',
                kwargs={'slug': cls.group.slug}
            ),
                'posts/group.html'),
            (reverse(
                'profile',
                kwargs={'username': cls.user}
            ),
                'posts/profile.html'),
            (reverse(
                'post_view',
                kwargs={
                    'username': cls.user,
                    'post_id': cls.post.pk
                }
            ),
                'posts/post.html'),
            (reverse('new_post'), 'posts/new.html',),
            (reverse(
                'post_edit',
                kwargs={
                    'username': cls.user,
                    'post_id': cls.post.pk
                }
            ),
                'posts/new.html',
            )
        )
        cls.cache_name = 'index_page'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    @override_settings(CACHES=TEST_CACHE_SETTING)
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client3 = Client()
        self.authorized_client.force_login(PagesTests.user)
        self.authorized_client2.force_login(PagesTests.user2)
        self.authorized_client3.force_login(PagesTests.user3)

    def check_post_in_context_correct(self, post):
        post_author_1 = post.author
        post_text_1 = post.text
        post_pub_group_1 = post.group
        post_image_1 = post.image
        self.assertEqual(post_author_1, PagesTests.user)
        self.assertEqual(post_text_1, PagesTests.post.text)
        self.assertEqual(str(post_pub_group_1), PagesTests.group.title)
        self.assertEqual(post_image_1, PagesTests.post.image)

    def test_pages_use_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        for adress, templates in PagesTests.all_urls:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, templates)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом и
        созданный пост появился на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][1]
        self.check_post_in_context_correct(first_object)

    def test_group_post_show_correct_context(self):
        """Шаблон group_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': {PagesTests.group.slug}})
        )
        self.assertEqual(response.context['group'].title,
                         PagesTests.group.title)
        self.assertEqual(response.context['group'].description,
                         PagesTests.post.text)
        self.assertEqual(response.context['group'].slug,
                         {PagesTests.group.slug})

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post  сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_post_show_correct_context(self):
        """На странице тестовой группы отображается пост группы"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': PagesTests.group.slug})
        )
        first_object = response.context['page'][1]
        self.check_post_in_context_correct(first_object)

    def test_profile_correct_context(self):
        """На странице профайл отображается пост с картинкой"""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': PagesTests.user})
        )
        first_object = response.context['page'][0]
        self.check_post_in_context_correct(first_object)

    def test_post_in_another_group_page(self):
        """На странице тестовой группы не отображается пост другой группы"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': PagesTests.group2.slug})
        )
        self.assertEqual(len(response.context['page']), 0)

    def test_post_edit_correct_context(self):
        """Страница редактирования поста
        сформирована с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': PagesTests.user,
                    'post_id': PagesTests.post.pk,
                }
            )
        )
        form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_page_correct_context(self):
        """Шаблон для страницы отдельного
        поста сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'post_view',
                kwargs={
                    'username': PagesTests.user,
                    'post_id': PagesTests.post.pk,
                }
            )
        )
        self.assertEqual(response.context['author'].username,
                         PagesTests.user.username)
        self.assertEqual(response.context['post'].text,
                         PagesTests.post.text)
        self.assertEqual(response.context['post'].image, PagesTests.post.image)

    def test_cache_page(self):
        """Проверка, что кеш главной страницы работает"""
        key = make_template_fragment_key('index_page')
        self.assertIsNotNone(key)

    def test_authorized_user_can_follow(self):
        """Проверка, что авторизованный пользователь может
        подписываться на других пользователей"""
        follow_count = Follow.objects.count()
        self.authorized_client.post(
            reverse('profile_follow', kwargs={'username': PagesTests.user2})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_authorized_user_can_unfollow(self):
        """Проверка, что авторизованный пользователь может
        отписываться от других пользователей"""
        self.authorized_client.post(
            reverse('profile_follow', kwargs={'username': PagesTests.user2})

        )
        follow_count = Follow.objects.count()
        self.authorized_client.post(
            reverse('profile_unfollow', kwargs={'username': PagesTests.user2})

        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_new_post_subscribe(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него."""
        """На странице тестовой группы не отображается пост другой группы"""
        self.authorized_client.post(
            reverse(
                'profile_follow',
                kwargs={'username': PagesTests.user2}
            )

        )
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 1)
        response = self.authorized_client3.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)


class PaginationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(username='GulyaevEO')
        cls.group = Group.objects.get(
            title='Тестовая группа',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Самый длинный тестовый пост',
            author=cls.user,
            group=cls.group,
        )

        post_list = [Post(
            text=f'Самый длинный тестовый пост{i}',
            author=cls.user,
            group=Group.objects.create(
                title=f'Тестовая группа{i}',
                description=f'Тестовый текст{i}',
                slug=f'test-slug{i}'
            )) for i in range(11)]
        Post.objects.bulk_create(post_list)


def setUp(self):
    self.authorized_client = Client()
    self.authorized_client.force_login(PaginationTests.user)


def test_username_page_correct_context(self):
    """Шаблон для username сформирован с
    правильным контекстом и пагинатор работает корректно."""
    response = self.authorized_client.get(
        reverse(
            'profile',
            kwargs={'username': str(PaginationTests.user)}
        )
    )
    self.assertEqual(
        response.context['author'].username,
        PaginationTests.user.username
    )
    self.assertEqual(len(response.context['page']), POST_PER_PAGE)
