from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal


class AdViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other_user = User.objects.create_user(username="user2", password="pass")
        self.ad = Ad.objects.create(
            user=self.user, title="T", description="D", category="B", condition="new"
        )

    def test_signup_get_form(self):
        """Проверяет, что при GET-запросе к странице регистрации возвращается форма."""
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_signup_post(self):
        """Проверяет успешную регистрацию нового пользователя и редирект на список объявлений."""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "Aa12345678!",
                "password2": "Aa12345678!",
            },
        )
        self.assertRedirects(response, reverse("ad_list"))

    def test_ad_create_get(self):
        """Проверяет, что авторизованный пользователь может получить форму создания объявления."""
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("ad_create"))
        self.assertEqual(response.status_code, 200)

    def test_create_ad_authenticated(self):
        """Проверяет, что авторизованный пользователь может создать объявление."""
        self.client.login(username="user1", password="pass")
        response = self.client.post(
            reverse("ad_create"),
            {
                "title": "New Ad",
                "description": "desc",
                "category": "Books",
                "condition": "used",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_create_ad_unauthenticated(self):
        """Проверяет, что неавторизованный пользователь не может создать объявление."""
        response = self.client.post(
            reverse("ad_create"),
            {"title": "X", "description": "Y", "category": "Toys", "condition": "new"},
        )
        self.assertNotEqual(response.status_code, 200)

    def test_ad_create_invalid_form(self):
        """Проверяет обработку невалидной формы создания объявления."""
        self.client.login(username="user1", password="pass")
        response = self.client.post(
            reverse("ad_create"),
            {
                "title": "",  # пустое поле
                "description": "desc",
                "category": "Books",
                "condition": "used",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_update_ad_by_owner(self):
        """Проверяет возможность обновления объявления его владельцем."""
        self.client.login(username="user1", password="pass")
        response = self.client.post(
            reverse("ad_edit", args=[self.ad.pk]),
            {
                "title": "Updated title",
                "description": "Updated",
                "category": "Books",
                "condition": "used",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, "Updated title")

    def test_update_ad_only_owner(self):
        """Проверяет, что пользователь не может изменить чужое объявление."""
        self.client.login(username="user2", password="pass")
        response = self.client.post(
            reverse("ad_edit", args=[self.ad.pk]),
            {"title": "Hacked title"},
        )
        self.assertEqual(response.status_code, 403)

    def test_ad_update_get(self):
        """Проверяет, что владелец может открыть страницу редактирования своего объявления."""
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("ad_edit", args=[self.ad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad.title)

    def test_ad_update_invalid_form(self):
        """Проверяет, что при невалидной форме редактирования страница возвращается с ошибками."""
        self.client.login(username="user1", password="pass")
        response = self.client.post(
            reverse("ad_edit", args=[self.ad.pk]),
            {"title": "", "description": "", "category": "", "condition": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_update_nonexistent_ad(self):
        """Проверяет, что редактирование несуществующего объявления возвращает 404."""
        self.client.login(username="user1", password="pass")
        response = self.client.post(reverse("ad_edit", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_ad(self):
        """Проверяет, что владелец может удалить своё объявление."""
        self.client.login(username="user1", password="pass")
        response = self.client.post(reverse("ad_delete", args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)

    def test_ad_list_view(self):
        """Проверяет доступность страницы списка объявлений."""
        response = self.client.get(reverse("ad_list"))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_category_and_condition(self):
        """Проверяет фильтрацию объявлений по категории и состоянию."""
        Ad.objects.create(
            user=self.user,
            title="Toy",
            description="desc",
            category="Toys",
            condition="used",
        )
        response = self.client.get(reverse("ad_list") + "?category=Toys&condition=used")
        self.assertContains(response, "Toy")
        self.assertNotContains(response, "Q")  # оригинальное объявление

    def test_search_by_keyword(self):
        """Проверяет поиск по ключевому слову в названии объявления."""
        Ad.objects.create(
            user=self.user,
            title="Rare Vintage Book",
            description="Very rare",
            category="Books",
            condition="used",
        )
        response = self.client.get(reverse("ad_list") + "?q=Vintage")
        self.assertContains(response, "Vintage")

    def test_pagination(self):
        """Проверяет, что пагинация объявлений работает корректно."""
        for i in range(15):
            Ad.objects.create(
                user=self.user,
                title=f"Ad {i}",
                description="desc",
                category="B",
                condition="used",
            )
        response = self.client.get(reverse("ad_list") + "?page=2")
        self.assertEqual(response.status_code, 200)


class ExchangeProposalViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender_user = User.objects.create_user(username="u1", password="pass")
        self.receiver_user = User.objects.create_user(username="u2", password="pass")

        self.ad1 = Ad.objects.create(
            user=self.sender_user,
            title="MyAd",
            description="D1",
            category="Books",
            condition="new",
        )
        self.ad2 = Ad.objects.create(
            user=self.receiver_user,
            title="OtherAd",
            description="D2",
            category="Toys",
            condition="used",
        )

    def test_proposal_creation(self):
        """Проверяет успешное создание предложения обмена между пользователями."""
        self.client.login(username="u1", password="pass")
        response = self.client.post(
            reverse("proposal_create"),
            {
                "ad_sender": self.ad1.id,
                "ad_receiver": self.ad2.id,
                "comment": "Lets swap",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_invalid_proposal_form(self):
        """Проверяет поведение при отправке невалидной формы предложения обмена."""
        self.client.login(username="u1", password="pass")
        response = self.client.post(
            reverse("proposal_create"),
            {"ad_sender": "", "ad_receiver": "", "comment": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ошибка при создании предложения.")

    def test_proposal_create_get(self):
        """Проверяет доступность формы создания предложения через GET-запрос."""
        self.client.login(username="u1", password="pass")
        response = self.client.get(
            reverse("proposal_create") + f"?ad_receiver_id={self.ad2.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_update_proposal_status(self):
        """Проверяет обновление статуса предложения получателем объявления."""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1, ad_receiver=self.ad2, comment="hi"
        )
        self.client.login(username="u2", password="pass")
        response = self.client.post(
            reverse("proposal_update", args=[proposal.id]), {"status": "accepted"}
        )
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, "accepted")

    def test_update_proposal_status_forbidden(self):
        """Проверяет, что пользователь не может обновить статус, если он не получатель предложения."""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1, ad_receiver=self.ad2, comment="hi"
        )
        self.client.login(username="u1", password="pass")  # не получатель
        response = self.client.post(
            reverse("proposal_update", args=[proposal.id]), {"status": "accepted"}
        )
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, "pending")  # не изменился
