from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random


VENDOR_NAMES = [
    ('Suresh', 'Patil', '+91 9876543210'),
    ('Ramesh', 'Jadhav', '+91 9876543211'),
    ('Ganesh', 'Shinde', '+91 9876543212'),
    ('Mahesh', 'More', '+91 9876543213'),
    ('Rajesh', 'Bhosale', '+91 9876543214'),
    ('Dinesh', 'Kulkarni', '+91 9876543215'),
    ('Santosh', 'Gaikwad', '+91 9876543216'),
    ('Prakash', 'Mane', '+91 9876543217'),
    ('Vijay', 'Kale', '+91 9876543218'),
    ('Anil', 'Deshmukh', '+91 9876543219'),
]

CUSTOMER_NAMES = [
    ('Priya', 'Desai', '+91 9123456780'),
    ('Anita', 'Kulkarni', '+91 9123456781'),
    ('Sunita', 'Sharma', '+91 9123456782'),
    ('Meena', 'Pawar', '+91 9123456783'),
    ('Kavita', 'Joshi', '+91 9123456784'),
]


class Command(BaseCommand):
    help = 'Seed demo data: customers, vendors, bookings, reviews'

    def handle(self, *args, **options):
        from accounts.models import User, VendorProfile, CustomerProfile
        from services.models import ServiceProblem, ServiceCategory
        from locations.models import Area
        from bookings.models import Booking, BookingStatusLog, Review

        self.stdout.write('Seeding demo data...')

        areas = list(Area.objects.filter(is_active=True)[:10])
        problems = list(ServiceProblem.objects.filter(is_active=True))

        if not areas:
            self.stdout.write(self.style.ERROR('Run seed_maharashtra first!'))
            return
        if not problems:
            self.stdout.write(self.style.ERROR('Run seed_services first!'))
            return

        # Create customers
        customers = []
        for i, (first, last, phone) in enumerate(CUSTOMER_NAMES):
            username = f'customer_{first.lower()}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': f'{username}@demo.sevasetu.in',
                    'phone_number': phone.replace(' ', ''),
                    'role': 'customer',
                    'preferred_language': random.choice(['mr', 'hi', 'en']),
                }
            )
            if created:
                user.set_password('demo@123')
                user.save()
                CustomerProfile.objects.get_or_create(user=user)
                self.stdout.write(f'  Customer: {username}')
            customers.append(user)

        # Create vendors
        vendors = []
        for i, (first, last, phone) in enumerate(VENDOR_NAMES):
            username = f'vendor_{first.lower()}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': f'{username}@demo.sevasetu.in',
                    'phone_number': phone.replace(' ', ''),
                    'role': 'vendor',
                    'preferred_language': random.choice(['mr', 'hi', 'en']),
                }
            )
            if created:
                user.set_password('demo@123')
                user.save()

            vp, vp_created = VendorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'aadhaar_number': ''.join([str(random.randint(0, 9)) for _ in range(12)]),
                    'is_verified': True,
                    'is_available': True,
                    'years_of_experience': random.randint(1, 10),
                    'wallet_balance': random.uniform(500, 5000),
                    'total_jobs_completed': random.randint(10, 200),
                    'rating': round(random.uniform(3.5, 5.0), 2),
                }
            )
            if vp_created and problems:
                vp.skills.set(random.sample(problems, min(len(problems), 5)))
            if vp_created and areas:
                vp.service_areas.set(random.sample(areas, min(len(areas), 3)))
            if created:
                self.stdout.write(f'  Vendor: {username}')
            vendors.append(user)

        # Create bookings
        statuses = [
            Booking.STATUS_REQUESTED,
            Booking.STATUS_VENDOR_ASSIGNED,
            Booking.STATUS_VENDOR_ACCEPTED,
            Booking.STATUS_IN_PROGRESS,
            Booking.STATUS_WORK_COMPLETED,
            Booking.STATUS_CLOSED,
            Booking.STATUS_CANCELLED,
        ]

        created_bookings = 0
        for i in range(20):
            customer = random.choice(customers)
            vendor = random.choice(vendors)
            problem = random.choice(problems)
            area = random.choice(areas)
            status = random.choice(statuses)
            days_offset = random.randint(-30, 7)
            pref_date = date.today() + timedelta(days=days_offset)

            booking = Booking.objects.create(
                customer=customer,
                vendor=vendor if status != Booking.STATUS_REQUESTED else None,
                problem=problem,
                area=area,
                address_line=f'House {random.randint(1,200)}, Demo Street',
                landmark='Near Main Road',
                status=status,
                preferred_date=pref_date,
                preferred_time_slot=random.choice(['morning', 'afternoon', 'evening']),
                description=f'Demo booking for {problem.title_en}',
                base_price=problem.base_price,
                total_price=problem.base_price,
                payment_method=random.choice(['cod', 'online']),
                payment_status='paid' if status == Booking.STATUS_CLOSED else 'pending',
            )
            BookingStatusLog.objects.create(
                booking=booking,
                from_status='',
                to_status=Booking.STATUS_REQUESTED,
                changed_by=customer,
            )
            created_bookings += 1

            if status == Booking.STATUS_CLOSED and vendor:
                Review.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'customer': customer,
                        'vendor': vendor,
                        'rating': random.randint(3, 5),
                        'review_text': random.choice([
                            'Very professional service!',
                            'Good work, on time.',
                            'Excellent! Highly recommended.',
                            'Quality work at fair price.',
                            'Quick and efficient service.',
                        ])
                    }
                )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data seeded! {len(customers)} customers, {len(vendors)} vendors, {created_bookings} bookings.'
        ))
        self.stdout.write('Login credentials: demo@123 for all demo accounts')
