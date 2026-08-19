from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date, time, datetime, timedelta
import json

from .models import Space, Customer, Booking, BlockedDate

class SpaceBookingTestCase(TestCase):
    def setUp(self):
        # Create spaces
        self.desk1 = Space.objects.create(
            name='Desk 1', category='Workspace', price_per_unit=5000.00,
            price_unit='day', min_duration=1, max_duration=1, capacity=1
        )
        self.desk2 = Space.objects.create(
            name='Desk 2', category='Workspace', price_per_unit=5000.00,
            price_unit='day', min_duration=1, max_duration=1, capacity=1
        )
        self.room_a = Space.objects.create(
            name='Room A', category='Meeting room', price_per_unit=10000.00,
            price_unit='hour', min_duration=1, max_duration=4, capacity=6
        )
        self.conference_room = Space.objects.create(
            name='Conference Room', category='Conference', price_per_unit=20000.00,
            price_unit='hour', min_duration=1, max_duration=4, capacity=20
        )

        # Create user
        self.user = User.objects.create_user(
            username='johndoe', email='john@example.com', password='password123',
            first_name='John', last_name='Doe'
        )
        # Create customer
        self.customer = Customer.objects.create(
            user=self.user, name='John Doe', email='john@example.com', phone='+2348011111111'
        )

        self.client = Client()

    def test_booking_auto_pricing(self):
        # Test auto pricing calculation on save
        booking = Booking(
            customer=self.customer,
            space=self.room_a,
            booking_date=date(2026, 8, 19),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration=2,
            status='Confirmed'
        )
        booking.save()
        self.assertEqual(booking.total_price, 20000.00)

    def test_duration_validations(self):
        # Test duration below minimum
        booking_short = Booking(
            customer=self.customer,
            space=self.room_a,
            booking_date=date(2026, 8, 19),
            start_time=time(10, 0),
            end_time=time(10, 30),
            duration=0.5, # Room A min is 1
            status='Confirmed'
        )
        with self.assertRaises(ValidationError):
            booking_short.save()

        # Test duration above maximum
        booking_long = Booking(
            customer=self.customer,
            space=self.room_a,
            booking_date=date(2026, 8, 19),
            start_time=time(10, 0),
            end_time=time(15, 0),
            duration=5, # Room A max is 4
            status='Confirmed'
        )
        with self.assertRaises(ValidationError):
            booking_long.save()

    def test_overlapping_room_bookings(self):
        # Book Room A from 10:00 to 12:00
        b1 = Booking.objects.create(
            customer=self.customer,
            space=self.room_a,
            booking_date=date(2026, 8, 19),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration=2,
            status='Confirmed'
        )

        # Attempt to book overlapping slot (11:00 to 13:00)
        url = reverse('check_availability')
        response = self.client.get(url, {
            'space_type': 'meeting_room_a',
            'date': '2026-08-19',
            'start_time': '11:00',
            'duration': '2'
        })
        data = json.loads(response.content)
        self.assertFalse(data['available'])
        self.assertIn("already booked", data['message'])

        # Attempt to book adjacent slot (12:00 to 14:00) - should be available
        response2 = self.client.get(url, {
            'space_type': 'meeting_room_a',
            'date': '2026-08-19',
            'start_time': '12:00',
            'duration': '2'
        })
        data2 = json.loads(response2.content)
        self.assertTrue(data2['available'])

    def test_blocked_date_availability(self):
        # Block Room A on August 20, 2026 full day
        BlockedDate.objects.create(
            space=self.room_a,
            date=date(2026, 8, 20),
            reason="Maintenance"
        )

        url = reverse('check_availability')
        response = self.client.get(url, {
            'space_type': 'meeting_room_a',
            'date': '2026-08-20',
            'start_time': '10:00',
            'duration': '2'
        })
        data = json.loads(response.content)
        self.assertFalse(data['available'])
        self.assertIn("fully blocked", data['message'])

    def test_hot_desk_allocation(self):
        # Book Desk 1 on Aug 19
        Booking.objects.create(
            customer=self.customer,
            space=self.desk1,
            booking_date=date(2026, 8, 19),
            start_time=time(9, 0),
            end_time=time(17, 0),
            duration=1,
            status='Confirmed'
        )

        # Check availability for Hot Desk - should allocate Desk 2
        url = reverse('check_availability')
        response = self.client.get(url, {
            'space_type': 'hot_desk',
            'date': '2026-08-19'
        })
        data = json.loads(response.content)
        self.assertTrue(data['available'])
        self.assertEqual(data['space_name'], 'Desk 2')

        # Book Desk 2 as well
        Booking.objects.create(
            customer=self.customer,
            space=self.desk2,
            booking_date=date(2026, 8, 19),
            start_time=time(9, 0),
            end_time=time(17, 0),
            duration=1,
            status='Confirmed'
        )

        # Check availability again - should now be fully booked
        response2 = self.client.get(url, {
            'space_type': 'hot_desk',
            'date': '2026-08-19'
        })
        data2 = json.loads(response2.content)
        self.assertFalse(data2['available'])
        self.assertIn("fully booked", data2['message'])

    def test_create_booking_api(self):
        # Authenticate first
        self.client.login(username='johndoe', password='password123')
        
        url = reverse('create_booking')
        payload = {
            'space_type': 'meeting_room_a',
            'date': '2026-08-19',
            'start_time': '10:00',
            'duration': '2',
            'phone': '+2348022222222'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['details']['space_name'], 'Room A')
        self.assertEqual(data['details']['customer_name'], 'John Doe')
        self.assertEqual(data['details']['customer_email'], 'john@example.com')
        
        # Verify Booking created in DB
        self.assertTrue(Booking.objects.filter(customer__user=self.user, space=self.room_a).exists())

    def test_create_booking_api_unauthenticated(self):
        url = reverse('create_booking')
        payload = {
            'space_type': 'meeting_room_a',
            'date': '2026-08-19',
            'start_time': '10:00',
            'duration': '2',
            'phone': '+2348022222222'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn("must be logged in", data['message'])

