from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='GulyaevEO')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """Для страниц author и tech используется
        соответствующая view функция."""
        templates_pages_names = {
            'author.html': reverse('author'),
            'tech.html': reverse('tech'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
