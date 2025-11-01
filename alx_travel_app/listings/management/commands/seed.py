import random
from django.core.management.base import BaseCommand
from listings.models import Listing, Booking, Review
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        # Create sample users
        users = [User.objects.create_user(username=fake.user_name(), email=fake.email(), password='password') for _ in range(5)]

        # Create listings
        for _ in range(10):
            listing = Listing.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                price_per_night=random.randint(50, 500),
                host=random.choice(users)
            )

            # Create bookings for each listing
            for _ in range(random.randint(1, 5)):
                booking = Booking.objects.create(
                    listing=listing,
                    user=random.choice(users),
                    start_date=fake.date_this_year(),
                    end_date=fake.date_this_year(),
                    status=random.choice(['pending', 'confirmed', 'canceled'])
                )

                # Create reviews for each booking
                for _ in range(random.randint(0, 3)):
                    Review.objects.create(
                        booking=booking,
                        rating=random.randint(1, 5),
                        comment=fake.text()
                    )
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
