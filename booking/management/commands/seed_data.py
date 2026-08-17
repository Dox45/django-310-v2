from django.core.management.base import BaseCommand
from booking.models import Space

class Command(BaseCommand):
    help = 'Seeds the database with initial Impact Hub Lagos spaces'

    def handle(self, *args, **options):
        spaces_data = [
            # Workspace / Hot Desks
            {
                'name': 'Desk 1',
                'category': 'Workspace',
                'price_per_unit': 5000.00,
                'price_unit': 'day',
                'min_duration': 1,
                'max_duration': 1,
                'capacity': 1,
                'description': 'Premium single workspace in our open-plan area. Includes high-speed Wi-Fi and power outlet.',
            },
            {
                'name': 'Desk 2',
                'category': 'Workspace',
                'price_per_unit': 5000.00,
                'price_unit': 'day',
                'min_duration': 1,
                'max_duration': 1,
                'capacity': 1,
                'description': 'Premium single workspace in our open-plan area. Includes high-speed Wi-Fi and power outlet.',
            },
            {
                'name': 'Desk 3',
                'category': 'Workspace',
                'price_per_unit': 5000.00,
                'price_unit': 'day',
                'min_duration': 1,
                'max_duration': 1,
                'capacity': 1,
                'description': 'Premium single workspace in our open-plan area. Includes high-speed Wi-Fi and power outlet.',
            },
            # Meeting Rooms
            {
                'name': 'Room A',
                'category': 'Meeting room',
                'price_per_unit': 10000.00,
                'price_unit': 'hour',
                'min_duration': 1,
                'max_duration': 4,
                'capacity': 6,
                'description': 'Professional meeting space equipped with an interactive display, whiteboard, and videoconferencing equipment.',
            },
            {
                'name': 'Room B',
                'category': 'Meeting room',
                'price_per_unit': 10000.00,
                'price_unit': 'hour',
                'min_duration': 1,
                'max_duration': 4,
                'capacity': 6,
                'description': 'Professional meeting space equipped with an interactive display, whiteboard, and videoconferencing equipment.',
            },
            # Conference Rooms
            {
                'name': 'Conference Room',
                'category': 'Conference',
                'price_per_unit': 20000.00,
                'price_unit': 'hour',
                'min_duration': 1,
                'max_duration': 4,
                'capacity': 20,
                'description': 'Spacious and high-end conference room equipped with a modern 4K projector, premium audio system, and climate control.',
            },
        ]

        for data in spaces_data:
            space, created = Space.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created space: {space.name}"))
            else:
                # Update existing records to match new details
                for key, val in data.items():
                    setattr(space, key, val)
                space.save()
                self.stdout.write(self.style.WARNING(f"Space: {space.name} already exists. Updated details."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed!"))
