from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Tag
from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """login is required to get tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@londonappdev.com',
            password='testpass',
            name='testname',
            )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='junkfood')
        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """tags returned for authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='test2@londonappdev.com',
            password='test2pass',
            name='test2name',
            )
        Tag.objects.create(user=user2, name='fruit')
        tag = Tag.objects.create(user=self.user, name='comfort food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
