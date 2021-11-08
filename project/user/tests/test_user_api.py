from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:users')

class PublicUserTest(TestCase):

  def setUp(self):
    self.client = APIClient()

  def test_create_user(self):
    """Test creating a user object and no password in response"""
    payload = {
      'username': 'test123',
      'password': 'test123!'
    }

    res = self.client.post(CREATE_USER_URL, payload)
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    user = get_user_model().objects.get(**res.data)
    self.assertTrue(user.check_password(payload['password']))
    self.assertNotIn(res.data, 'password')
