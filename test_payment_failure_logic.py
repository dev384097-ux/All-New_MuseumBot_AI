import unittest
from unittest.mock import MagicMock, patch
from app import app
import json

class TestPaymentFailureLogic(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.rzp_client')
    @patch('app.get_db_connection')
    def test_check_payment_status_failed(self, mock_db, mock_rzp):
        # Mock session
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'Test User'

        # Mock Razorpay Link Fetch (Terminal Failure)
        mock_pl = {
            'status': 'cancelled',
            'order_id': 'order_123'
        }
        mock_rzp.payment_link.fetch.return_value = mock_pl

        # Test request
        response = self.app.post('/api/check_payment_status', 
                                 data=json.dumps({
                                     'payment_link_id': 'plink_123',
                                     'museum': 'National Museum',
                                     'visitor_name': 'Test User',
                                     'total': 100
                                 }),
                                 content_type='application/json')
        
        data = json.loads(response.data.decode())
        self.assertTrue(data['success'])
        self.assertFalse(data['paid'])
        self.assertEqual(data['status'], 'cancelled')
        self.assertIn('cancelled', data['message'])

    @patch('app.rzp_client')
    @patch('app.get_db_connection')
    def test_check_payment_status_payment_attempt_failed(self, mock_db, mock_rzp):
        # Mock session
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'Test User'

        # Mock Razorpay Link Fetch (Still created)
        mock_pl = {
            'status': 'created',
            'order_id': 'order_123'
        }
        mock_rzp.payment_link.fetch.return_value = mock_pl

        # Mock Razorpay Payments (Recent failed)
        mock_payments = {
            'items': [
                {
                    'status': 'failed',
                    'error_description': 'Customer opted for failure'
                }
            ]
        }
        mock_rzp.payment.all.return_value = mock_payments

        # Test request
        response = self.app.post('/api/check_payment_status', 
                                 data=json.dumps({
                                     'payment_link_id': 'plink_123',
                                     'museum': 'National Museum',
                                     'visitor_name': 'Test User',
                                     'total': 100
                                 }),
                                 content_type='application/json')
        
        data = json.loads(response.data.decode())
        self.assertTrue(data['success'])
        self.assertFalse(data['paid'])
        self.assertEqual(data['status'], 'failed')
        self.assertEqual(data['message'], 'Customer opted for failure')

if __name__ == '__main__':
    unittest.main()
