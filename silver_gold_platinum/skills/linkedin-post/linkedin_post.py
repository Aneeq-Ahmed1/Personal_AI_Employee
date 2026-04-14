import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_linkedin_person_urn(access_token):
    """Get the person URN for the authenticated user"""
    url = "https://api.linkedin.com/v2/me"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('id')
        return None
    except Exception:
        return None

def post_to_linkedin(post_text, post_title="", post_url=""):
    """Post content to LinkedIn based on the provided parameters"""

    # Validate required fields
    if not post_text:
        return {
            'success': False,
            'error': 'Post text is required'
        }

    # Get LinkedIn credentials from environment variables
    linkedin_access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    linkedin_page_id = os.getenv('LINKEDIN_PAGE_ID')
    use_personal_profile = os.getenv('LINKEDIN_USE_PERSONAL_PROFILE', 'false').lower() == 'true'

    if not linkedin_access_token:
        return {
            'success': False,
            'error': 'LinkedIn access token not configured in environment variables'
        }

    # Determine author URN
    author_urn = None
    if use_personal_profile:
        # Get personal profile URN
        person_id = get_linkedin_person_urn(linkedin_access_token)
        if person_id:
            author_urn = f"urn:li:person:{person_id}"
        else:
            return {
                'success': False,
                'error': 'Could not retrieve personal profile URN. Check token permissions.'
            }
    elif linkedin_page_id:
        # Use company page URN
        author_urn = f"urn:li:organization:{linkedin_page_id}"
    else:
        return {
            'success': False,
            'error': 'Either LINKEDIN_PAGE_ID or LINKEDIN_USE_PERSONAL_PROFILE must be configured'
        }

    # Construct the post content
    full_post = post_text
    if post_title:
        full_post = f"{post_title}\n\n{full_post}"
    if post_url:
        full_post += f"\n\nLearn more: {post_url}"

    # Prepare headers for LinkedIn API
    headers = {
        'Authorization': f'Bearer {linkedin_access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    # Prepare the payload for LinkedIn API
    linkedin_payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": full_post
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Make the API call to LinkedIn
    api_url = "https://api.linkedin.com/v2/ugcPosts"
    try:
        response = requests.post(api_url, headers=headers, json=linkedin_payload)

        if response.status_code != 201:
            return {
                'success': False,
                'error': f'LinkedIn API returned status {response.status_code}: {response.text}'
            }

        return {
            'success': True,
            'message': 'LinkedIn post created successfully',
            'details': {
                'title': post_title,
                'text': post_text,
                'url': post_url
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }