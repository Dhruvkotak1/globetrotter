import unittest
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models import User, City, Activity, Trip, TripStop, TripActivity, CustomExpense

class GlobeTrotterTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_landing_page(self):
        """Screen 2: Home Dashboard / Landing Page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GlobeTrotter', response.data)
        self.assertIn(b'Plan a New Trip', response.data)

    def test_auth_flows(self):
        """Screen 1 & 2: Login, Signup, Forgot Password, Reset Password"""
        # 1. Login page
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Welcome Back', res.data)

        # 2. Perform valid login
        res = self.client.post('/login', data={
            'identifier': 'traveler@globetrotter.com',
            'password': 'travel123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'My Travel Itineraries', res.data)

        # 3. Profile view (Screen 12)
        res = self.client.get('/profile')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Preplanned Trips', res.data)

        # 4. Logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 5. Forgot password
        res = self.client.get('/forgot-password')
        self.assertEqual(res.status_code, 200)

    def test_city_and_activity_search(self):
        """Screens 7 & 8: City Search & Activity Search"""
        # City search
        res = self.client.get('/cities?q=Tokyo')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Tokyo', res.data)

        # Activity search
        res = self.client.get('/activities?category=Sightseeing')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Sightseeing', res.data)

        # API cities search
        res = self.client.get('/api/cities/search?q=Paris')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Paris', res.data)

    def test_trips_and_itinerary_builder(self):
        """Screens 3, 4, 5, 6, 9, 10: Trip CRUD, Builder, Timeline, Budget & Calendar"""
        # Login first
        self.client.post('/login', data={
            'identifier': 'traveler@globetrotter.com',
            'password': 'travel123'
        })

        # Screen 4: Trips list
        res = self.client.get('/trips/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Wonders of Japan', res.data)

        # Screen 3: Create Trip Page
        res = self.client.get('/trips/new')
        self.assertEqual(res.status_code, 200)

        # Create new trip
        res = self.client.post('/trips/new', data={
            'title': 'Test Australian Outback Journey',
            'description': 'Exploring Sydney and the Great Barrier Reef',
            'start_date': (date.today() + timedelta(days=20)).isoformat(),
            'end_date': (date.today() + timedelta(days=27)).isoformat(),
            'target_budget': '3200',
            'visibility': 'public'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test Australian Outback Journey', res.data)

        with self.app.app_context():
            trip = Trip.query.filter_by(title='Test Australian Outback Journey').first()
            self.assertIsNotNone(trip)
            trip_id = trip.id

        # Screen 5: Builder Screen
        res = self.client.get(f'/trips/{trip_id}/builder')
        self.assertEqual(res.status_code, 200)

        # Screen 6: Itinerary View Screen
        res = self.client.get(f'/trips/{trip_id}/itinerary')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Day-by-Day Journey Flow', res.data)

        # Screen 9: Budget & Cost Breakdown Screen
        res = self.client.get(f'/trips/{trip_id}/budget')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Expense Breakdown by Category', res.data)

        # Screen 10: Calendar Screen
        res = self.client.get(f'/trips/{trip_id}/calendar')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Trip Visual Calendar', res.data)

    def test_community_and_shared_trip(self):
        """Screens 10 & 11: Community Hub & Shared View with Clone"""
        # Community Hub
        res = self.client.get('/community')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Explore Shared Travel Itineraries', res.data)

        # Public / Shared Itinerary View (Screen 11)
        res = self.client.get('/trip/shared/japan-golden-route-2026')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Shared Travel Plan', res.data)

    def test_admin_dashboard(self):
        """Screen 13: Admin / Analytics Dashboard"""
        # Non-admin access should be forbidden/redirected
        self.client.post('/login', data={
            'identifier': 'traveler@globetrotter.com',
            'password': 'travel123'
        })
        res = self.client.get('/admin/', follow_redirects=True)
        self.assertIn(b'Access denied', res.data)

        # Admin login
        self.client.get('/logout')
        self.client.post('/login', data={
            'identifier': 'admin@globetrotter.com',
            'password': 'admin123'
        })
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Platform Analytics & Administration', res.data)
        self.assertIn(b'User Management', res.data)

if __name__ == '__main__':
    unittest.main()
