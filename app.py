import json
import requests

def lambda_handler(event, context):
    """
    Main Lambda handler for Felix & Pearl Bot.
    Processes incoming messages and sends them to Discord.
    """
    try:
        # Parse the incoming event
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Invalid JSON: {str(e)}'})
            }
            
        content = body.get('content', '')
        webhook_url = body.get('webhook_url', '')
        
        if not content or not webhook_url:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required fields: content and webhook_url')
            }
        
        # Send the message
        success, error_message = send_message(content, webhook_url)
        
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Failed to send message: {error_message}')
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent successfully')
        }
        
    except Exception as e:
        print(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def send_message(content, webhook_url):
    """
    Send a message using the provided Discord webhook URL.
    Returns (success, error_message) tuple.
    
    Args:
        content (str): The message content to send
        webhook_url (str): The Discord webhook URL
    """
    try:
        response = requests.post(
            webhook_url,
            json={'content': content},
            timeout=10
        )
        
        if response.status_code == 204:
            return True, None
        else:
            return False, f'HTTP {response.status_code}'
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False, str(e) 