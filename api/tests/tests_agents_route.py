from api.tests.TestCase import TestCase, PermissionUtilities

from rest_framework import status
from rest_framework.test import APIClient

from logs.models import User, Agent

class AgentRouteCase(TestCase, PermissionUtilities):
    invalid_agent = {
        'name': 'name' + 'n' * 256,
        'environment': 'invalid_environment'
    }

    simple_valid_agent = {
        'name': 'A simple valid agent',
        'environment': 'testing'
    }

    full_valid_agent = {
        'name': 'A full valid agent',
        'environment': 'production',
        'address': '127.0.0.1'
        # user declared in setUp()
    }

    route = '/api/agents/'

    def setUp(self):
        self.client = APIClient()
        self.create_users_with_permissions(Agent)

        self.agents_list = []
        users_list = []

        self.agents_list.append(Agent.objects.create(environment='testing', name='agent 0'))
        for i, env in enumerate(['development', 'testing', 'production']):
            user = User.objects.create(username=f'user{i+1}', email=f'user{i+1}@email.com')
            agent = Agent.objects.create(environment=env, name=f'agent {i+1}', user=user)
            self.agents_list.append(agent)
            users_list.append(user)

        self.full_valid_agent['user'] = users_list[0].id

    def test_list_agents(self):
        response = self.client.get(f'{self.route}')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.get(f'{self.route}')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='view')
        response = self.client.get(f'{self.route}')
        with self.subTest('Must return data and a success code', response=response):
            agents = response.json()
            for i, agent in enumerate(agents):
                expected_agent = self.agents_list[i]
                self.assertEqual(expected_agent.name, agent.get('name'))
                self.assertEqual(expected_agent.environment, agent.get('environment'))
                self.assertEqual(expected_agent.user_id, agent.get('user'))

    def test_create_agent(self):
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='add')
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Name and environment must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('required', body.get('name'))
            self.assertSubstringIn('required', body.get('environment'))

        response = self.client.post(f'{self.route}', data=self.invalid_agent, format='json')
        with self.subTest('Name and environment must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('Ensure', body.get('name'))
            self.assertSubstringIn('valid', body.get('environment'))

        data = self.simple_valid_agent
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Agent must be created with only required fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            agent = response.json()
            self.assertEqual(data.get('name'), agent.get('name'))
            self.assertEqual(data.get('environment'), agent.get('environment'))

            expected_agents = len(self.agents_list) + 1
            db_agents = Agent.objects.count()
            self.assertEqual(expected_agents, db_agents)

        data = self.full_valid_agent
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Agent must be created with all fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            agent = response.json()
            self.assertEqual(data.get('name'), agent.get('name'))
            self.assertEqual(data.get('environment'), agent.get('environment'))
            self.assertEqual(data.get('user'), agent.get('user'))
            self.assertEqual(data.get('address'), agent.get('address'))

            expected_agents = len(self.agents_list) + 2
            db_agents = Agent.objects.count()
            self.assertEqual(expected_agents, db_agents)

    def test_list_one_agent(self):
        pk = len(self.agents_list) + 2

        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='view')
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

        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='change')
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Name and environment must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('required', body.get('name'))
            self.assertSubstringIn('required', body.get('environment'))

        data = self.invalid_agent
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Name and environment must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertIn('environment', body)
            self.assertSubstringIn('Ensure', body.get('name'))
            self.assertSubstringIn('valid', body.get('environment'))

        data = self.full_valid_agent
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

        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='change')
        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Partial update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        data = {'name': self.invalid_agent.get('name')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Name must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('Ensure', body.get('name'))

        pk = 2
        data = {'environment': self.invalid_agent.get('environment')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Environment must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('environment', body)
            self.assertSubstringIn('valid', body.get('environment'))

        pk = 2
        data = {'address': 'invalid_address'}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Address must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('address', body)
            self.assertSubstringIn('valid', body.get('address'))

        pk = 2
        data = {'user': 20}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('User must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('user', body)
            self.assertSubstringIn('valid', body.get('user'))

        pk = 2
        data = {'address': self.full_valid_agent.get('address')}
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
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='add')
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='delete')
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
