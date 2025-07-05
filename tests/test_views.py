from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal


class AdViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', password='pass')
        self.other_user = User.objects.create_user(username='user2', password='pass')
        self.ad = Ad.objects.create(user=self.user, title='T', description='D', category='B', condition='new')

    def test_create_ad_authenticated(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('ad_create'), {
            'title': 'New Ad', 'description': 'desc', 'category': 'Books', 'condition': 'used'
        })
        self.assertEqual(response.status_code, 302)

    def test_create_ad_unauthenticated(self):
        response = self.client.post(reverse('ad_create'), {
            'title': 'X', 'description': 'Y', 'category': 'Toys', 'condition': 'new'
        })
        self.assertNotEqual(response.status_code, 200)

    def test_update_ad_by_owner(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('ad_edit', args=[self.ad.pk]), {
            'title': 'Updated title',
            'description': 'Updated',
            'category': 'Books',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated title')

    def test_update_ad_only_owner(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(reverse('ad_edit', args=[self.ad.pk]), {
            'title': 'Hacked title'
        })
        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_ad(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('ad_edit', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_ad(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('ad_delete', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)

    def test_ad_list_view(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_category_and_condition(self):
        Ad.objects.create(user=self.user, title='Toy', description='desc', category='Toys', condition='used')
        response = self.client.get(reverse('ad_list') + '?category=Toys&condition=used')
        self.assertContains(response, 'Toy')
        self.assertNotContains(response, 'Q')  # оригинальное объявление

    def test_search_by_keyword(self):
        Ad.objects.create(user=self.user, title='Rare Vintage Book', description='Very rare', category='Books', condition='used')
        response = self.client.get(reverse('ad_list') + '?q=Vintage')
        self.assertContains(response, 'Vintage')

    def test_pagination(self):
        for i in range(15):
            Ad.objects.create(user=self.user, title=f'Ad {i}', description='desc', category='B', condition='used')
        response = self.client.get(reverse('ad_list') + '?page=2')
        self.assertEqual(response.status_code, 200)


class ExchangeProposalViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender_user = User.objects.create_user(username='u1', password='pass')
        self.receiver_user = User.objects.create_user(username='u2', password='pass')

        self.ad1 = Ad.objects.create(user=self.sender_user, title='MyAd', description='D1', category='Books',
                                     condition='new')
        self.ad2 = Ad.objects.create(user=self.receiver_user, title='OtherAd', description='D2', category='Toys',
                                     condition='used')

    def test_proposal_creation(self):
        self.client.login(username='u1', password='pass')
        response = self.client.post(reverse('proposal_create'), {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad2.id,
            'comment': 'Lets swap'
        })
        self.assertEqual(response.status_code, 302)

    def test_update_proposal_status(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='hi')
        self.client.login(username='u2', password='pass')
        response = self.client.post(reverse('proposal_update', args=[proposal.id]), {
            'status': 'accepted'
        })
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')
