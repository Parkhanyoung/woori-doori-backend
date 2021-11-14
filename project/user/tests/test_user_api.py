from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

USERS_URL = reverse('user:user')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def user_create(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test creating a user object and no password in response"""
        payload = {
            'username': 'test123',
            'password': 'test123!'
            }
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_already_exist(self):
        """Test creating a user already exists fails"""
        payload = {
            'username': 'test123',
            'password': 'test123!'
        }
        user_create(**payload)
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_wrong_id(self):
        """Test creating a user with wrong username fails"""
        payload = {
            'username': '12345',
            'password': 'test123'
        }
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_wrong_pw(self):
        """Test creating a user with wrong PW fails"""
        payload = {
            'username': 'test123',
            'password': '12345'
        }
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class UserTokenTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_token(self):
        """Test creating a token with valid credentials succeeds"""
        payload = {
            'username': 'test123',
            'password': 'test123'
        }
        user_create(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test creating a token with invalid credentials fails"""
        payload = {
            'username': 'test123',
            'password': 'test123'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = user_create(username='test123', password='test123!')
        self.client.force_authenticate(self.user)

    def test_create_profile(self):
        """Test creating a profile with correct datas succeeds"""
        payload = {
            'nickname': 'testnickname',
            'gender': 'man'
        }
        res = self.client.post(PROFILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_profile_fails(self):
        """Test creating a profile without nickname fails"""
        res = self.client.post(PROFILE_URL, {'gender': '남자'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
