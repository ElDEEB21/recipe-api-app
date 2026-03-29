"""
Django command to wait for the database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Django command to wait for the database to be available."""

    help = 'Wait for database to be available'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--max-retries',
            type=int,
            default=30,
            help='Maximum number of retries (default: 30)',
        )
        parser.add_argument(
            '--wait-interval',
            type=float,
            default=1.0,
            help='Seconds to wait between retries (default: 1.0)',
        )

    def handle(self, *args, **options):
        """Entrypoint for command."""
        max_retries = options['max_retries']
        wait_interval = options['wait_interval']

        self.stdout.write('Waiting for database...')
        retries = 0

        while retries < max_retries:
            try:
                self.check(databases=['default'])
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except (Psycopg2Error, OperationalError):
                retries += 1
                self.stdout.write(
                    f'Database unavailable, retry {retries}/{max_retries}...'
                )
                time.sleep(wait_interval)

        self.stdout.write(
            self.style.ERROR(f'Database not available after {max_retries} retries')
        )
        raise SystemExit(1)
