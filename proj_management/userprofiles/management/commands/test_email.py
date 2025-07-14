from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email functionality for member invitations'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to test')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            # Check if user exists
            user = User.objects.get(email=email)
            
            self.stdout.write(
                self.style.SUCCESS(f'Found user: {user.get_full_name()} ({user.username})')
            )
            
            # Test password reset email
            reset_form = PasswordResetForm({'email': email})
            if reset_form.is_valid():
                reset_form.save(
                    use_https=False,  # For testing
                    email_template_name='registration/password_reset_email.html',
                    subject_template_name='registration/password_reset_subject.txt'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Password reset email sent to {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Email validation failed: {reset_form.errors}')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ No user found with email: {email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            ) 