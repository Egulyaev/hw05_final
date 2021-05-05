from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='GulyaevEO')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_pages(self):
        """Запрошенные страницы author и tech
        доступны неавторизованному пользователю"""
        code_url_names = {
            200: (
                '/about/author/',
                '/about/tech/',
            )
        }

        for code, adress in code_url_names.items():
            for item in adress:
                with self.subTest(adress=item):
                    response = self.guest_client.get(item)
                    self.assertEqual(response.status_code, code)

    def test_about_pages_used_correct_template(self):
        """Страницы author и tech использует соответствующий шаблон."""

        templates_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
