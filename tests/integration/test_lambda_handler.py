import os
import json
import pytest
from unittest.mock import patch, MagicMock
import boto3
from moto import mock_aws
from lambda_function import lambda_handler
from app import lambda_handler as app_lambda_handler

# Set AWS region for tests
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def mock_env():
    """Fixture to set up test environment variables."""
    test_env = {
        'ANTHROPIC_API_KEY': 'test_key',
        'FELIX_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'PEARL_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'WEATHER_API_KEY': 'test_weather_key',
        'WEATHER_LOCATION': 'Test City,TS,US',
        'BIRTHDAYS_CONFIG': json.dumps({
            "04-16": {"name": "Test Person"}
        }),
        'TEST_MODE': 'true'
    }
    with patch.dict(os.environ, test_env):
        yield test_env

@pytest.fixture
def mock_claude():
    """Fixture to mock Claude API responses."""
    with patch('lambda_function.claude') as mock:
        mock.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Test message")]
        )
        yield mock

@pytest.fixture
def mock_requests():
    """Fixture to mock requests for weather and national days."""
    with patch('lambda_function.requests') as mock:
        # Mock weather response
        mock.get.return_value = MagicMock(
            json=lambda: {
                'main': {
                    'temp': 72,
                    'feels_like': 70,
                    'humidity': 50
                },
                'weather': [{'description': 'sunny'}],
                'wind': {'speed': 5},
                'sys': {
                    'sunrise': 1234567890,
                    'sunset': 1234567890
                }
            },
            status_code=200
        )
        yield mock

@pytest.fixture
def mock_send_discord():
    """Fixture to mock Discord message sending."""
    with patch('lambda_function.send_discord_message') as mock:
        mock.return_value = "test_message_id"
        yield mock

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope="function")
def dynamodb_table(aws_credentials):
    """Create a mock DynamoDB table."""
    with mock_aws():
        # Create the DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName='test-failed-messages',
            KeySchema=[
                {'AttributeName': 'message_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'message_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        yield table

def test_lambda_handler_normal_day(mock_env, mock_claude, mock_requests, mock_send_discord):
    """Test Lambda handler on a normal day."""
    event = {"test_mode": True}
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    assert mock_send_discord.call_count == 1

def test_lambda_handler_birthday(mock_env, mock_claude, mock_requests):
    """Test lambda handler with a birthday event."""
    # Mock Claude response
    mock_claude.messages.create.return_value.content = [type('obj', (object,), {'text': 'Test message'})]
    
    # Mock requests response
    mock_requests.post.return_value.status_code = 204
    
    # Test event
    event = {
        'test_mode': True,
        'test_date': '04-16'  # Felix's birthday
    }
    
    # Call lambda handler
    response = lambda_handler(event, None)
    
    # Check response
    assert response['statusCode'] == 200
    
    # Check that Claude was called for birthday messages
    assert mock_claude.messages.create.call_count >= 2

def test_lambda_handler_error_handling(mock_env, mock_claude, mock_requests, mock_send_discord):
    """Test Lambda handler error handling."""
    mock_send_discord.side_effect = Exception("API Error")
    
    event = {"test_mode": True}
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    assert "API Error" in json.loads(response['body'])

def test_lambda_handler_weather_error(mock_env, mock_claude, mock_requests, mock_send_discord):
    """Test Lambda handler when weather API fails."""
    # Make weather API raise an exception
    def mock_get(*args, **kwargs):
        if 'weather' in args[0]:
            raise Exception("Weather API Error")
        return MagicMock(text="<html></html>")  # Mock response for national days
    
    mock_requests.get.side_effect = mock_get
    
    event = {"test_mode": True}
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    assert "Weather API Error" in json.loads(response['body'])

def test_app_lambda_handler_failed_message(mock_env, dynamodb_table, mock_requests, mock_uuid, mock_datetime):
    """Test app Lambda handler with failed message sending."""
    # Mock requests to simulate a failed message
    mock_requests.post.return_value = MagicMock(status_code=500)
    
    event = {
        'body': json.dumps({
            'content': 'Test message',
            'webhook_url': 'https://discord.com/api/webhooks/test',
            'message_type': 'weather'
        })
    }
    
    response = app_lambda_handler(event, None)
    
    # Check response
    assert response['statusCode'] == 202
    assert json.loads(response['body']) == 'Message queued for retry'
    
    # Check that message was stored in DynamoDB
    items = dynamodb_table.scan()['Items']
    assert len(items) == 1
    item = items[0]
    assert item['message_id'] == 'test-uuid'
    assert item['retry_count'] == 0
    assert item['content'] == 'Test message'
    assert item['webhook_url'] == 'https://discord.com/api/webhooks/test'
    assert item['message_type'] == 'weather'
    assert item['error_message'] == 'HTTP 500'

