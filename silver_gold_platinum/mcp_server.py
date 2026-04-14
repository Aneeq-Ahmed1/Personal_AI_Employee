from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import json

# Add the skills directory to the path so we can import the skills
skills_path = Path(__file__).parent / "skills"
sys.path.append(str(skills_path / "email-send"))
sys.path.append(str(skills_path / "linkedin-post"))
sys.path.append(str(skills_path / "human-approval"))

# Import the skills
from email_send import send_email
from linkedin_post import post_to_linkedin
from human_approval import check_approval_needed

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    """Send an email based on the JSON payload"""
    try:
        data = request.get_json()

        # Check if this action needs approval
        if not check_approval_needed('send_email', data):
            return jsonify({
                'success': False,
                'message': 'Action rejected by user approval'
            }), 400

        # Extract email details from the payload
        recipient = data.get('recipient')
        subject = data.get('subject', 'No Subject')
        body = data.get('body', '')

        # Call the email-send skill
        result = send_email(recipient, subject, body)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/post_linkedin', methods=['POST'])
def post_linkedin_endpoint():
    """Post content to LinkedIn based on the JSON payload"""
    try:
        data = request.get_json()

        # Check if this action needs approval
        if not check_approval_needed('post_linkedin', data):
            return jsonify({
                'success': False,
                'message': 'Action rejected by user approval'
            }), 400

        # Extract post details from the payload
        post_text = data.get('text', '')
        post_title = data.get('title', '')
        post_url = data.get('url', '')

        # Call the linkedin-post skill
        result = post_to_linkedin(post_text, post_title, post_url)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp_endpoint():
    """Send a WhatsApp message based on the JSON payload"""
    try:
        data = request.get_json()

        # Check if this action needs approval
        if not check_approval_needed('send_whatsapp', data):
            return jsonify({
                'success': False,
                'message': 'Action rejected by user approval'
            }), 400

        # Extract message details from the payload
        phone_number = data.get('phone_number')
        message = data.get('message', '')

        if not phone_number or not message:
            return jsonify({'error': 'Phone number and message are required'}), 400

        # Get WhatsApp credentials from environment variables
        whatsapp_access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        whatsapp_phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

        if not whatsapp_access_token or not whatsapp_phone_number_id:
            return jsonify({'error': 'WhatsApp credentials not configured in environment variables'}), 500

        # Prepare headers for WhatsApp API
        headers = {
            'Authorization': f'Bearer {whatsapp_access_token}',
            'Content-Type': 'application/json'
        }

        # Prepare the payload for WhatsApp API
        whatsapp_payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        # Make the API call to WhatsApp
        api_url = f"https://graph.facebook.com/v18.0/{whatsapp_phone_number_id}/messages"
        import requests
        response = requests.post(api_url, headers=headers, json=whatsapp_payload)

        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'WhatsApp API returned status {response.status_code}: {response.text}'
            }), 500

        return jsonify({
            'success': True,
            'message': f'WhatsApp message sent successfully to {phone_number}',
            'details': {
                'phone_number': phone_number,
                'message': message
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/trigger_task', methods=['POST'])
def trigger_task():
    """Trigger a custom task based on the JSON payload"""
    try:
        data = request.get_json()

        # Check if this action needs approval
        if not check_approval_needed('trigger_task', data):
            return jsonify({
                'success': False,
                'message': 'Action rejected by user approval'
            }), 400

        # Extract task details from the payload
        task_name = data.get('task_name')
        task_params = data.get('params', {})

        if not task_name:
            return jsonify({'error': 'Task name is required'}), 400

        # Process the task based on its name
        if task_name == 'create_todo':
            # Example task: Create a TODO file in the Inbox
            from datetime import datetime

            if 'title' not in task_params or 'content' not in task_params:
                return jsonify({'error': 'Title and content are required for create_todo task'}), 400

            # Create a new markdown file in the Inbox
            import os
            from pathlib import Path

            inbox_path = Path("vault") / "Inbox"
            inbox_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_{timestamp}_{task_params['title'].replace(' ', '_')}.md"
            filepath = inbox_path / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {task_params['title']}\n\n")
                f.write(f"## Description\n{task_params['content']}\n\n")
                f.write(f"## Created\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            return jsonify({
                'success': True,
                'message': f'Task "{task_params["title"]}" created successfully',
                'details': {
                    'task': task_name,
                    'filepath': str(filepath)
                }
            })

        else:
            return jsonify({
                'success': False,
                'error': f'Unknown task: {task_name}'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MCP Server',
        'endpoints': [
            '/send_email',
            '/post_linkedin',
            '/send_whatsapp',
            '/trigger_task'
        ]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)