from django.test import TestCase as DjangoTestCase
from django.test.testcases import safe_repr

from logs.models import User, Permission

class PermissionUtilities:
    def login(self, permission='all'):
        credentials = self.permission_users[permission]
        response = self.client.post('/api/login/', data=credentials, format='json')
        if response.status_code != 200:
            print(response.json(), credentials)
            print(User.objects.get(username=self.permission_users[permission]['username']))

        self.assertEqual(response.status_code, 200)
        token = response.json().get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def create_users_with_permissions(self, model):
        """Create users with different permissions for a given model"""
        self.assertIsNotNone(model)
        model_name = model._meta.model_name

        User.objects.create_superuser('all', 'all@email.com', 'all')
        self.permission_users = {
            'all': {'username': 'all', 'password': 'all'}
        }
        for permission in ['view', 'add', 'change', 'delete']:
            user = User.objects.create(
                username=permission,
                email=f'{permission}@email.com',
            )
            user.set_password(permission)
            user.save()

            codename = f'{permission}_{model_name}'
            user.user_permissions.set([Permission.objects.get(codename=codename)])

            self.permission_users[permission] = {
                'username': permission, 'password': permission
            }


class TestCase(DjangoTestCase):
    def assertSubstringIn(self, substring, container, msg=None):
        """Check if substring matches at least one item in container"""
        result = any(substring in item for item in container)
        if not result:
            msg = self._formatMessage(
                msg, f'{substring} is not substring in {safe_repr(container)}'
            )
            self.fail(msg)
