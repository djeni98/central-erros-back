from django.test import TestCase as DjangoTestCase
from django.test.testcases import safe_repr

class TestCase(DjangoTestCase):
    def assertSubstringIn(self, substring, container, msg=None):
        """Check if substring matches at least one item in container"""
        result = any(substring in item for item in container)
        if not result:
            msg = self._formatMessage(
                msg, f'{substring} is not substring in {safe_repr(container)}'
            )
            self.fail(msg)
