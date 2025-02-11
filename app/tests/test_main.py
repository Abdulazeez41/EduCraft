import unittest
from app import app

class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage_loads(self):
        """Test that the homepage loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Educraft', response.data)

    def test_dashboard_access(self):
        """Test dashboard accessibility."""
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in', response.data)

if __name__ == '__main__':
    unittest.main()
