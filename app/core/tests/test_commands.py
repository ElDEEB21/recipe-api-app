"""
Tests for the custom management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg20pError  # type: ignore
import django.core.management
from django.db.utils import OperationalError
from django.test import SimpleTestCase


class CommandTests(SimpleTestCase):
    """Tests for the custom management commands."""

    @patch('core.management.commands.wait_for_db.Command.check')
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database when database is available."""
        patched_check.return_value = True

        django.core.management.call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    @patch('core.management.commands.wait_for_db.Command.check')
    def test_wait_for_db_delay(self, patched_check, patched_sleep):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = [
            Psycopg20pError] * 2 + [OperationalError] * 3 + [True]

        django.core.management.call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
