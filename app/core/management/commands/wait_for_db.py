"""
Django command to wait for the database to be available.
"""

import time
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg20pError # type: ignore

class Command(BaseCommand):
    """Django command to wait for the database to be available."""

    def handle(self, *args, **options):
        """Entrypoint for the command."""
        self.stdout.write('Waiting for database...')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg20pError, OperationalError) as e:
                self.stdout.write(f'Database unavailable, waiting 1 second... ({e})')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))