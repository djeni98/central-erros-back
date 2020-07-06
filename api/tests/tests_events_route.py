from api.tests.TestCase import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from datetime import datetime

from logs.models import User, Agent, Event


class EventRouteCase(TestCase):
    invalid_event = {
        'level': 'invalid_level',
        'description': True,
        'details': True
    }

    simple_valid_event = {
        'level': 'DEBUG',
        'description': 'A simple valid description',
        'details': 'A simple valid detail'
    }

    full_valid_event = {
        'level': 'CRITICAL',
        'description': 'A simple valid description',
        'details': 'A simple valid detail',
        'datetime': datetime.now(),
        'archived': False
        # user declared in setUp()
        # agent declared in setUp()
    }

    route = '/api/events/'

    def setUp(self):
        self.client = APIClient()
        self.events_list = []
        agents_list = []
        users_list = []

        for i, level in enumerate(['CRITICAL', 'DEBUG', 'ERROR', 'WARNING', 'INFO']):
            user = User.objects.create(username=f'user{i+1}', email=f'user{i+1}@email.com')
            agent = Agent.objects.create(environment='testing', name=f'agent {i+1}', user=user)
            event = Event.objects.create(
                level=level, agent=agent, user=user,
                description=f'Event description {i+1}',
                details=f'Event details {i+1}'
            )
            self.events_list.append(event)
            agents_list.append(agent)
            users_list.append(user)

        item = agents_list[-1]
        event = Event.objects.create(level='INFO', agent=item, description='only agent', details='details: only agent')
        self.events_list.append(event)

        item = users_list[-1]
        event = Event.objects.create(level='WARNING', user=item, description='only user', details='details: only user')
        self.events_list.append(event)

        event = Event.objects.create(level='ERROR', description='no user, no agent', details='details: no user, no agent')
        self.events_list.append(event)
        
        self.full_valid_event['agent'] = agents_list[0].id
        self.full_valid_event['user'] = users_list[0].id

    def test_list_events(self):
        response = self.client.get(f'{self.route}')
        events = response.json()

        all_fields = ['id', 'level', 'description', 'details', 'datetime', 'archived', 'source', 'collected_by']
        for i, event in enumerate(events):
            expected_event = self.events_list[i]
            for field in all_fields:
                self.assertEqual(getattr(expected_event, field), event.get(field))

            self.assertEqual(expected_event.user_id, event.get('user'))
            self.assertEqual(expected_event.agent_id, event.get('agent'))

    def test_create_event(self):
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Level, description and details must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('level', body)
            self.assertIn('description', body)
            self.assertIn('details', body)
            self.assertSubstringIn('required', body.get('level'))
            self.assertSubstringIn('required', body.get('description'))
            self.assertSubstringIn('required', body.get('details'))

        response = self.client.post(f'{self.route}', data=self.invalid_event, format='json')
        with self.subTest('Level, description and details must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('level', body)
            self.assertIn('description', body)
            self.assertIn('details', body)
            self.assertSubstringIn('valid', body.get('level'))
            self.assertSubstringIn('valid', body.get('description'))
            self.assertSubstringIn('valid', body.get('details'))

        data = self.simple_valid_event
        response = self.client.post(f'{self.route}', data=data, format='json')
        check_in_fields = ['id', 'datetime', 'archived', 'source', 'collected_by']
        with self.subTest('Event must be created with only required fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            event = response.json()

            for field in check_in_fields:
                self.assertIn(field, event)

            self.assertEqual(data.get('level'), event.get('level'))
            self.assertEqual(data.get('description'), event.get('description'))
            self.assertEqual(data.get('details'), event.get('details'))

            expected_events = len(self.events_list) + 1
            db_events = Event.objects.count()
            self.assertEqual(expected_events, db_events)

        data = self.full_valid_event
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Event must be created with all fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            event = response.json()
            
            check_fields = list(data.keys())
            check_fields.remove('datetime') # Datetime in python doesn't have 'Z' at end
            for field in check_fields:
                self.assertEqual(data.get(field), event.get(field))

            expected_events = len(self.events_list) + 2
            db_events = Event.objects.count()
            self.assertEqual(expected_events, db_events)

    def test_list_one_event(self):
        pk = len(self.events_list) + 2
        response = self.client.get(f'{self.route}{pk}/')

        with self.subTest('List must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return the correct event', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            event = response.json()
            expected_event = self.events_list[pk-1]
            self.assertEqual(pk, event.get('id'))
            self.assertEqual(expected_event.id, event.get('id'))
            self.assertEqual(expected_event.level, event.get('level'))
            self.assertEqual(expected_event.description, event.get('description'))
            self.assertEqual(expected_event.details, event.get('details'))

    def test_update_event(self):
        pk = len(self.events_list) + 2
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Level, description and details must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('level', body)
            self.assertIn('description', body)
            self.assertIn('details', body)
            self.assertSubstringIn('required', body.get('level'))
            self.assertSubstringIn('required', body.get('description'))
            self.assertSubstringIn('required', body.get('details'))
        
        data = self.invalid_event
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Level, description and details must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('level', body)
            self.assertIn('description', body)
            self.assertIn('details', body)
            self.assertSubstringIn('valid', body.get('level'))
            self.assertSubstringIn('valid', body.get('description'))
            self.assertSubstringIn('valid', body.get('details'))

        data = self.full_valid_event
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Agent must be updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            event = response.json()
            expected_event = self.events_list[pk-1]
            self.assertEqual(pk, event.get('id'))
            self.assertEqual(expected_event.id, event.get('id'))

            for field in ['level', 'description', 'details', 'archived', 'user', 'agent']:
                self.assertEqual(data.get(field), event.get(field))

            self.assertNotEqual(expected_event.details, event.get('details'))
            self.assertNotEqual(expected_event.description, event.get('description'))

    def test_partial_update_event(self):
        pk = len(self.events_list) + 2
        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Partial update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        data = {'level': self.invalid_event.get('level')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Level must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('level', body)
            self.assertSubstringIn('valid', body.get('level'))

        pk = 2
        data = {'description': self.invalid_event.get('description')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Description must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('description', body)
            self.assertSubstringIn('valid', body.get('description'))

        pk = 2
        data = {'details': self.invalid_event.get('details')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Details must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('details', body)
            self.assertSubstringIn('valid', body.get('details'))

        pk = 2
        data = {'datetime': 'invalid_datetime'}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Datetime must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('datetime', body)
            self.assertSubstringIn('wrong format', body.get('datetime'))

        pk = 2
        data = {'agent': 20}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Agent must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('agent', body)
            self.assertSubstringIn('valid', body.get('agent'))

        pk = 2
        data = {'user': 20}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('User must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('user', body)
            self.assertSubstringIn('valid', body.get('user'))

        pk = 2
        data = {'archived': 20}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Archived must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('archived', body)
            self.assertSubstringIn('valid', body.get('archived'))

        pk = 2
        data = {'archived': True}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Event must be partial updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            event = response.json()
            expected_event = self.events_list[pk-1]
            self.assertEqual(pk, event.get('id'))
            self.assertEqual(expected_event.id, event.get('id'))
            self.assertEqual(expected_event.level, event.get('level'))
            self.assertEqual(expected_event.description, event.get('description'))
            self.assertEqual(expected_event.details, event.get('details'))
            self.assertEqual(expected_event.agent.id, event.get('agent'))
            self.assertEqual(expected_event.user.id, event.get('user'))
            self.assertEqual(expected_event.source, event.get('source'))
            self.assertEqual(expected_event.collected_by, event.get('collected_by'))

            self.assertEqual(data.get('archived'), event.get('archived'))
            self.assertNotEqual(expected_event.archived, event.get('archived'))

    def test_delete_event(self):
        pk = len(self.events_list) + 2
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Delete must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Event must be deleted', response=response):
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            total_events = len(self.events_list) - 1
            db_events = Event.objects.count()
            self.assertEqual(total_events, db_events)
            self.assertRaises(Event.DoesNotExist, Event.objects.get, pk=pk)
