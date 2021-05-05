from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Самый длинный тестовый пост',
            author=User.objects.create_user(username='GulyaevEO')
        )

    def test_str(self):
        """__str__  совпадает с ожидаемым."""
        post = PostModelTest.post
        expected_text = post.text[:15]
        self.assertEquals(expected_text, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Имя тестовой группы',
            description='Тестовое описание группы',
        )

    def test_str(self):
        """__str__  совпадает с ожидаемым."""
        group = GroupModelTest.group
        expected_text = group.title
        self.assertEqual(str(group), expected_text)
