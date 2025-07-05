from django.test import TestCase
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal


class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')

    def test_create_ad(self):
        ad = Ad.objects.create(
            user=self.user,
            title='Test Item',
            description='A good item',
            category='Books',
            condition='new'
        )
        self.assertEqual(ad.title, 'Test Item')
        self.assertEqual(ad.user.username, 'testuser')
        self.assertIsNotNone(ad.created_at)

    def test_ad_str(self):
        ad = Ad.objects.create(
            user=self.user,
            title='Cool Book',
            description='D',
            category='Books',
            condition='used'
        )
        self.assertEqual(str(ad), 'Cool Book')


class ExchangeProposalModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1')
        self.ad1 = Ad.objects.create(user=self.user, title='A1', description='D1', category='Books', condition='used')
        self.ad2 = Ad.objects.create(user=self.user, title='A2', description='D2', category='Toys', condition='new')

    def test_create_proposal(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Wanna trade!'
        )
        self.assertEqual(proposal.status, 'pending')
        self.assertIsNotNone(proposal.created_at)

    def test_proposal_str(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Swap!'
        )
        expected = f'{self.ad1} → {self.ad2} ({proposal.status})'
        self.assertEqual(str(proposal), expected)
