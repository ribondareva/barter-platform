from django.contrib.auth.models import User
from django.test import TestCase
from ads.forms import AdForm, ExchangeProposalForm
from ads.models import Ad


class AdFormTest(TestCase):
    def test_valid_form(self):
        """Проверка валидной формы объявления."""
        form = AdForm(
            data={
                "title": "T",
                "description": "D",
                "category": "Books",
                "condition": "new",
            }
        )
        self.assertTrue(form.is_valid())

    def test_missing_title(self):
        """Форма должна быть невалидна при отсутствии названия объявления."""
        form = AdForm(
            data={
                "title": "",
                "description": "D",
                "category": "Books",
                "condition": "new",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_missing_all_fields(self):
        """Форма должна быть невалидна при отсутствии всех обязательных полей."""
        form = AdForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("category", form.errors)
        self.assertIn("condition", form.errors)


class ProposalFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="p1")
        self.user2 = User.objects.create_user(username="u2", password="p2")

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title="A1",
            description="D1",
            category="Books",
            condition="new",
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title="A2",
            description="D2",
            category="Toys",
            condition="used",
        )

    def test_valid_proposal_form(self):
        """Проверка валидной формы обмена между двумя пользователями."""
        form = ExchangeProposalForm(
            data={
                "ad_sender": self.ad1.id,
                "ad_receiver": self.ad2.id,
                "comment": "Trade",
            }
        )
        self.assertTrue(form.is_valid())

    def test_empty_comment_if_required(self):
        """Проверка, что пустой комментарий вызывает ошибку валидации."""
        form = ExchangeProposalForm(data={"comment": ""})
        self.assertFalse(form.is_valid())

    def test_same_ad_exchange_not_allowed(self):
        """Проверка, что обмен одного и того же объявления невозможен."""
        form = ExchangeProposalForm(
            data={
                "ad_sender": self.ad1.id,
                "ad_receiver": self.ad1.id,
                "comment": "Invalid",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_same_user_exchange_not_allowed(self):
        """Проверка, что пользователь не может обмениваться своими же объявлениями."""
        ad3 = Ad.objects.create(
            user=self.user1,
            title="A3",
            description="D3",
            category="Music",
            condition="used",
        )
        form = ExchangeProposalForm(
            data={"ad_sender": self.ad1.id, "ad_receiver": ad3.id, "comment": "Invalid"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
