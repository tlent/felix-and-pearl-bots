import json
import pytest
from unittest.mock import patch, MagicMock

# Import the app function
from app import lambda_handler, send_message

@pytest.fixture
def mock_requests():
    """Fixture to mock requests for sending messages."""
    with patch('app.requests') as mock:
        # Mock successful response
        mock.post.return_value = MagicMock(status_code=204)
        yield mock

def test_lambda_handler_success(mock_requests):
    """Test app function with successful message sending."""
    event = {
        'body': json.dumps({
            'content': 'Test message',
            'webhook_url': 'https://discord.com/api/webhooks/test'
        })
    }
    
    response = lambda_handler(event, None)
    
    # Check response
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'Message sent successfully'
    
    # Check that requests.post was called
    mock_requests.post.assert_called_once_with(
        'https://discord.com/api/webhooks/test',
        json={'content': 'Test message'},
        timeout=10
    )

def test_lambda_handler_failed_message(mock_requests):
    """Test app function with failed message sending."""
    # Mock requests to simulate a failed message
    mock_requests.post.return_value = MagicMock(status_code=500)
    
    event = {
        'body': json.dumps({
            'content': 'Test message',
            'webhook_url': 'https://discord.com/api/webhooks/test'
        })
    }
    
    response = lambda_handler(event, None)
    
    # Check response
    assert response['statusCode'] == 500
    assert 'Failed to send message' in json.loads(response['body'])

def test_lambda_handler_invalid_json(mock_requests):
    """Test app function with invalid JSON in the event body."""
    event = {
        'body': 'invalid json'
    }
    
    response = lambda_handler(event, None)
    
    # Check response
    assert response['statusCode'] == 400
    error_body = json.loads(response['body'])
    assert 'error' in error_body
    assert 'Invalid JSON' in error_body['error']

def test_send_message_success():
    """Test send_message function with successful response."""
    with patch('app.requests') as mock_req:
        mock_req.post.return_value = MagicMock(status_code=204)
        
        result = send_message('Test message', 'https://discord.com/api/webhooks/test')
        
        assert result is True
        mock_req.post.assert_called_once_with(
            'https://discord.com/api/webhooks/test',
            json={'content': 'Test message'},
            timeout=10
        )

def test_send_message_failure():
    """Test send_message function with failed response."""
    with patch('app.requests') as mock_req:
        mock_req.post.return_value = MagicMock(status_code=500)
        
        result = send_message('Test message', 'https://discord.com/api/webhooks/test')
        
        assert result is False
        mock_req.post.assert_called_once()

def test_send_message_exception():
    """Test send_message function with exception."""
    with patch('app.requests') as mock_req:
        mock_req.post.side_effect = Exception("Test exception")
        
        result = send_message('Test message', 'https://discord.com/api/webhooks/test')
        
        assert result is False
        mock_req.post.assert_called_once() 