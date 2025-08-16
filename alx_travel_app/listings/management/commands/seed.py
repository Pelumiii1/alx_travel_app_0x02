from django.core.management.base import BaseCommand
from listings.models import User, Listing, Booking, Review
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Seeding data...'))

       
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.all().delete()

        # Create users
        host = User.objects.create_user(
            email='host@example.com',
            password='password123',
            first_name='Host',
            last_name='User',
            phone_number='1234567890',
            role='host'
        )

        guest = User.objects.create_user(
            email='guest@example.com',
            password='password123',
            first_name='Guest',
            last_name='User',
            phone_number='0987654321',
            role='guest'
        )

        # Create properties
        for i in range(3):
            prop = Listing.objects.create(
                host=host,
                name=f'Lovely Stay {i+1}',
                description='A beautiful place to stay.',
                location='Lagos',
                price_per_night=random.randint(50, 200)
            )

            # Create bookings for each property
            for j in range(2):
                start_date = timezone.now().date() + timedelta(days=j * 5)
                end_date = start_date + timedelta(days=3)
                total_price = (end_date - start_date).days * prop.price_per_night

                booking = Booking.objects.create(
                    property=prop,
                    user=guest,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_price,
                    status='confirmed'
                )

                # Add reviews
                Review.objects.create(
                    property=prop,
                    user=guest,
                    rating=random.randint(3, 5),
                    comment='Great experience!',
                )


        self.stdout.write(self.style.SUCCESS('Seeding complete ✅'))
