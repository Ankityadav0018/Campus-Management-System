from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.resources.models import CampusFaculty


class Command(BaseCommand):
    help = 'Sync existing faculty users with CampusFaculty table'

    def handle(self, *args, **options):
        faculty_users = User.objects.filter(role='faculty')
        
        created_count = 0
        updated_count = 0
        
        for user in faculty_users:
            try:
                # Check if CampusFaculty record exists with this email
                faculty, created = CampusFaculty.objects.get_or_create(
                    email=user.email,
                    defaults={
                        'faculty_id': f"FAC{str(CampusFaculty.objects.count() + 1).zfill(4)}",
                        'name': user.get_full_name() or user.email.split('@')[0],
                        'user': user
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created faculty profile for {user.email}')
                    )
                else:
                    # Update the user link if it doesn't exist
                    if not faculty.user:
                        faculty.user = user
                        faculty.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Linked existing faculty profile for {user.email}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠ Faculty profile already exists for {user.email}')
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {user.email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Sync complete! Created: {created_count}, Updated: {updated_count}')
        )
