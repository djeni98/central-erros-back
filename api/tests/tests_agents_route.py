from django.test import TestCase
from django.test.testcases import safe_repr

from rest_framework import status
from rest_framework.test import APIClient

from datetime import datetime, timezone, timedelta

from logs.models import User, Agent


class AgentRouteCase(TestCase):
    valid_name = 'A valid agent'
    valid_environment = 'testing'
    valid_address = '127.0.0.1'
    # valid_user declared in setUp()

    invalid_name = True
    invalid_environment = 'invalid_environment'
    invalid_address = 'invalid_address'
    invalid_user = 10.101

    route = '/api/agents/'

    def assertSubstringIn(self, substring, container, msg=None):
        """Check if substring matches at least one item in container"""
        result = any(substring in item for item in container)
        if not result:
            msg = self._formatMessage(
                msg, f'{substring} is not substring in {safe_repr(container)}'
            )
            self.fail(msg)

    def setUp(self):
        self.client = APIClient()
        self.agents_list = []
        self.users_list = []

        for i, env in enumerate(['development', 'testing', 'production']):
            user = User.objects.create(username=f'user{i+1}', email=f'user{i+1}@email.com')
            agent = Agent.objects.create(environment=env, name=f'agent {i+1}', user=user)
            self.agents_list.append(agent)
            self.users_list.append(user)

        self.valid_user = self.users_list[0]

    def test_list_agents(self):
        response = self.client.get(f'{self.route}')
        agents = response.json()

        for i, agent in enumerate(agents):
            expected_agent = self.agents_list[i]
            self.assertEqual(expected_agent.name, agent.get('name'))
            self.assertEqual(expected_agent.environment, agent.get('environment'))
            self.assertEqual(expected_agent.user_id, agent.get('user'))

    def test_create_agent(self):
        data = {'address': self.valid_address}
        response = self.client.post(f'{self.route}', data=data, format='json')

        with self.subTest('Name and environment must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('required', body.get('name'))
            self.assertSubstringIn('required', body.get('environment'))

        data = {'name': self.invalid_name, 'environment': self.invalid_environment}
        response = self.client.post(f'{self.route}', data=data, format='json')

        with self.subTest('Name and environment must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('valid', body.get('name'))
            self.assertSubstringIn('valid', body.get('environment'))

        data = {
            'name': self.valid_name,
            'environment': self.valid_environment,
            'user': self.valid_user.id,
            'address': self.valid_address
        }
        response = self.client.post(f'{self.route}', data=data, format='json')

        with self.subTest('Agent must be created', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            agent = response.json()
            self.assertEqual(data.get('name'), agent.get('name'))
            self.assertEqual(data.get('environment'), agent.get('environment'))
            self.assertEqual(data.get('user'), agent.get('user'))
            self.assertEqual(data.get('address'), agent.get('address'))

            expected_agents = len(self.agents_list) + 1
            db_agents = Agent.objects.count()
            self.assertEqual(expected_agents, db_agents)

    def test_list_one_agent(self):
        pk = len(self.agents_list) + 2
        response = self.client.get(f'{self.route}{pk}/')

        with self.subTest('List must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return the correct agent', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            agent = response.json()
            expected_agent = self.agents_list[pk-1]
            self.assertEqual(pk, agent.get('id'))
            self.assertEqual(expected_agent.id, agent.get('id'))
            self.assertEqual(expected_agent.name, agent.get('name'))
            self.assertEqual(expected_agent.environment, agent.get('environment'))

    def test_update_agent(self):
        pk = len(self.agents_list) + 2
        data = {}
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        data = {'address': self.valid_address}
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Name and environment must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('required', body.get('name'))
            self.assertSubstringIn('required', body.get('environment'))

        data = {'name': self.invalid_name, 'environment': self.invalid_environment}
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Name and environment must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('valid', body.get('name'))
            self.assertSubstringIn('valid', body.get('environment'))

        data = {
            'name': self.valid_name,
            'environment': self.valid_environment,
            'user': self.valid_user.id,
            'address': self.valid_address
        }
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Agent must be updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            agent = response.json()
            expected_agent = self.agents_list[pk-1]
            self.assertEqual(pk, agent.get('id'))
            self.assertEqual(expected_agent.id, agent.get('id'))
            self.assertEqual(data.get('name'), agent.get('name'))
            self.assertEqual(data.get('environment'), agent.get('environment'))
            self.assertEqual(data.get('user'), agent.get('user'))
            self.assertEqual(data.get('address'), agent.get('address'))
            self.assertNotEqual(expected_agent.name, agent.get('name'))

    def test_partial_update_agent(self):
        pk = len(self.agents_list) + 2
        data = {}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Partial update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        data = {'name': self.invalid_name}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Name must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('valid', body.get('name'))

        pk = 2
        data = {'environment': self.invalid_environment}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Environment must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('environment', body)
            self.assertSubstringIn('valid', body.get('environment'))

        pk = 2
        data = {'address': self.invalid_address}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Address must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('address', body)
            self.assertSubstringIn('valid', body.get('address'))

        pk = 2
        data = {'user': self.invalid_user}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('User must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('user', body)
            self.assertSubstringIn('valid', body.get('user'))

        pk = 2
        data = {'address': self.valid_address}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')

        with self.subTest('Agent must be partial updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            agent = response.json()
            expected_agent = self.agents_list[pk-1]
            self.assertEqual(pk, agent.get('id'))
            self.assertEqual(expected_agent.id, agent.get('id'))
            self.assertEqual(expected_agent.name, agent.get('name'))
            self.assertEqual(expected_agent.environment, agent.get('environment'))
            self.assertEqual(expected_agent.user.id, agent.get('user'))

            self.assertEqual(data.get('address'), agent.get('address'))
            self.assertNotEqual(expected_agent.address, agent.get('address'))

    def test_delete_agent(self):
        pk = len(self.agents_list) + 2
        response = self.client.delete(f'{self.route}{pk}/')

        with self.subTest('Delete must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        response = self.client.delete(f'{self.route}{pk}/')

        with self.subTest('Agent must be deleted', response=response):
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            total_agents = len(self.agents_list) - 1
            db_agents = Agent.objects.count()
            self.assertEqual(total_agents, db_agents)
            self.assertRaises(Agent.DoesNotExist, Agent.objects.get, pk=pk)
