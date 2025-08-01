from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from userprofiles.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile objects for users who don\'t have them'

    def handle(self, *args, **options):
        self.stdout.write('Creating UserProfile objects for existing users...')
        
        # Get all users
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            # Check if user already has a UserProfile
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(f'  - Created UserProfile for user: {user.username}')
                created_count += 1
            else:
                self.stdout.write(f'  - UserProfile already exists for: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} UserProfile objects!')) 