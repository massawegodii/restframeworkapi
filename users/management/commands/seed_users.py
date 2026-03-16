import random
from django.core.management.base import BaseCommand
from users.models import User
from faker import Faker

class Command(BaseCommand):
    help = "Seed users for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=100,
            help='Number of users to create'
        )

    def handle(self, *args, **options):
        fake = Faker()
        total = options['total']
        roles = ['admin', 'manager', 'customer']

        users_created = 0

        for _ in range(total):
            email = fake.unique.email()
            firstname = fake.first_name()
            lastname = fake.last_name()
            role = random.choice(roles)
            password = "123"  

            try:
                User.objects.create_user(
                    email=email,
                    firstname=firstname,
                    lastname=lastname,
                    password=password,
                    role=role
                )
                users_created += 1
            except Exception as e:
                print(f"Skipping {email}: {e}")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {users_created} users'))