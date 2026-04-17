import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add the project directory to sys.path
sys.path.append(os.getcwd())

with patch('razorpay.Client') as MockClient:
    # Setup mock
    mock_rzp = MockClient.return_value
    mock_rzp.payment_link.fetch.return_value = {'status': 'cancelled'}
    
    from app import app
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            
        response = client.post('/api/check_payment_status', 
                               data=json.dumps({
                                   'payment_link_id': 'plink_test',
                                   'museum': 'Test Museum',
                                   'visitor_name': 'Test Visitor',
                                   'visit_date': '2026-04-18',
                                   'count': 1,
                                   'total': 100
                               }),
                               content_type='application/json')
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Data: {response.get_data(as_text=True)}")
        
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert data['paid'] is False
        assert data['status'] == 'cancelled'
        print("Backend Verification Successful!")
