from api.tests.TestCase import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from logs.models import User


class RegisterRouteCase(TestCase):
    invalid_user = {
        'username': 'denis' + 'd' * 150,
        'email': 'denisemailcom',
        'password': '1234567890'
    }

    simple_valid_user = {
        'username': 'denise',
        'email': 'denise@email.com',
        'password': 'MYPASSWORD_myp455w0rd',
    }

    full_valid_user = {
        'username': 'denis',
        'email': 'denis@email.com',
        'password': 'MYPASSWORD_myp455w0rd',
        'first_name': 'Denis',
        'last_name': 'Lastname'
    }

    check_fields = ['username', 'email', 'first_name', 'last_name']
    route = '/api/register/'

    def setUp(self):
        self.client = APIClient()

    def test_invalid_register(self):
        response = self.client.post(self.route, data={}, format='json')
        with self.subTest('Username, email and password must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('required', body.get('username'))
            self.assertSubstringIn('required', body.get('email'))
            self.assertSubstringIn('required', body.get('password'))

        response = self.client.post(self.route, data=self.invalid_user, format='json')
        with self.subTest('User fields must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('Ensure', body.get('username'))
            self.assertSubstringIn('valid', body.get('email'))
            self.assertSubstringIn('common', body.get('password'))
            self.assertSubstringIn('numeric', body.get('password'))

    def test_valid_register(self):
        data = self.simple_valid_user
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('User must be registered with only required fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user = response.json()

            self.assertEqual(data.get('email'), user.get('email'))
            self.assertEqual(data.get('username'), user.get('username'))

            db_users = User.objects.count()
            self.assertEqual(1, db_users)

        data = self.full_valid_user
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('User must be registered with all fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user = response.json()

            for field in self.check_fields:
                self.assertEqual(data.get(field), user.get(field))

            db_users = User.objects.count()
            self.assertEqual(2, db_users)
        
    def test_permissions_must_not_be_registered(self):
        data = dict(self.full_valid_user)
        data['is_superuser'] = True
        response = self.client.post(self.route, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = response.json()

        for field in self.check_fields:
            self.assertEqual(data.get(field), user.get(field))

        self.assertNotEqual(data.get('is_superuser'), user.get('is_superuser'))
        db_users = User.objects.count()
        self.assertEqual(1, db_users)
