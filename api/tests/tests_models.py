from django.test import TestCase
from datetime import datetime, timezone, timedelta

from api.models import User, Agent, Event

class ModelsTestCase(TestCase):
    def create_user(self, name):
        password = f'senha{name}'
        user = User.objects.create(
            name=name, email=f'{name}@email.com', password=password
        )
        user.set_password(password)
        user.save()
        return user

    def setUp(self):
        # Users
        bruna = self.create_user('bruna')
        carla = self.create_user('carla')
        denis = self.create_user('denis')
        lucas = self.create_user('lucas')

        maria = User.objects.create(email='maria@email.com')
        maria.set_password('maria')
        maria.save()

        # Agents
        localhost = Agent.objects.create(
            environment='development', name='localhost'
        )
        simple_app = Agent.objects.create(
            environment='testing', name='Simple app', user=bruna
        )
        blog = Agent.objects.create(
            environment='production', name='www.blog.com', user=denis
        )

        # Events
        now = datetime.now(timezone(timedelta(hours=-3)))
        info = Event.objects.create(
            level='INFO', description='new user registered',
            datetime=now, details='new user abcd registered today',
            agent=blog
        )
        warning = Event.objects.create(
            level='WARNING', description='node upgrade available',
            datetime=now, details='new upgrade available',
            agent=localhost, user=lucas
        )
        debug = Event.objects.create(
            level='DEBUG', description='console log json',
            datetime=now, details='{"itens": [2343, 1119, 1345]}',
            agent=simple_app, user=carla
        )
        error = Event.objects.create(
            level='ERROR', description='RunTimeError: unexpected token',
            datetime=now, details='Received } before "',
            agent=localhost, user=maria
        )
        critical = Event.objects.create(
            level='CRITICAL', description='shutdow',
            datetime=now, details='forced reboot made by user',
            agent=simple_app
        )

    def test_users_must_have_email_and_password(self):
        users = User.objects.all()
        for user in users:
            self.assertIsNotNone(user.email)
            self.assertIsNotNone(user.password)
            self.assertIsNot(user.email, '')
            self.assertIsNot(user.password, '')

    def test_agents_must_have_name_and_environment(self):
        agents = Agent.objects.all()
        for agent in agents:
            self.assertIsNotNone(agent.name)
            self.assertIsNotNone(agent.environment)
            self.assertIsNot(agent.name, '')
            self.assertIsNot(agent.environment, '')

    def test_events_source_returns_agent_name(self):
        events = [
            ('www.blog.com', Event.objects.get(level='INFO')),
            ('localhost', Event.objects.get(level='WARNING')),
            ('Simple app', Event.objects.get(level='DEBUG')),
            ('localhost', Event.objects.get(level='ERROR')),
            ('Simple app', Event.objects.get(level='CRITICAL')),
        ]

        for source, event in events:
            self.assertEqual(source, event.source)

    def test_events_collectedBy_returns_user_name_or_email(self):
        events = [
            (None, Event.objects.get(level='INFO')),
            ('lucas', Event.objects.get(level='WARNING')),
            ('carla', Event.objects.get(level='DEBUG')),
            ('maria@email.com', Event.objects.get(level='ERROR')),
            (None, Event.objects.get(level='CRITICAL')),
        ]

        for user, event in events:
            self.assertEqual(user, event.collected_by)
