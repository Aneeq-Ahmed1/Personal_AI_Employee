"""
Social Media MCP Server - Gold Tier
Unified integration for Facebook, Instagram, Twitter/X, and LinkedIn.
Allows posting, monitoring, and analytics across all platforms.
"""

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('social_media_mcp_server')

app = Flask(__name__)

# Social Media API Configuration
FACEBOOK_CONFIG = {
    'app_id': os.getenv('FACEBOOK_APP_ID', ''),
    'app_secret': os.getenv('FACEBOOK_APP_SECRET', ''),
    'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', ''),
    'page_id': os.getenv('FACEBOOK_PAGE_ID', ''),
}

INSTAGRAM_CONFIG = {
    'app_id': os.getenv('INSTAGRAM_APP_ID', ''),
    'app_secret': os.getenv('INSTAGRAM_APP_SECRET', ''),
    'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
    'business_account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', ''),
}

TWITTER_CONFIG = {
    'api_key': os.getenv('TWITTER_API_KEY', ''),
    'api_secret': os.getenv('TWITTER_API_SECRET', ''),
    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', ''),
    'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
    'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''),
}

LINKEDIN_CONFIG = {
    'client_id': os.getenv('LINKEDIN_CLIENT_ID', ''),
    'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET', ''),
    'access_token': os.getenv('LINKEDIN_ACCESS_TOKEN', ''),
    'organization_id': os.getenv('LINKEDIN_ORGANIZATION_ID', ''),
}


def post_to_facebook(message, link=None, photo_url=None):
    """
    Post to Facebook Page.
    
    Args:
        message: Post text
        link: Optional link to share
        photo_url: Optional photo URL
    
    Returns:
        dict: Post result
    """
    if not FACEBOOK_CONFIG['access_token'] or not FACEBOOK_CONFIG['page_id']:
        return {'success': False, 'error': 'Facebook credentials not configured'}
    
    url = f"https://graph.facebook.com/v18.0/{FACEBOOK_CONFIG['page_id']}/feed"
    
    params = {
        'message': message,
        'access_token': FACEBOOK_CONFIG['access_token']
    }
    
    if link:
        params['link'] = link
    
    if photo_url:
        params['picture'] = photo_url
    
    try:
        response = requests.post(url, data=params, timeout=30)
        result = response.json()
        
        if response.status_code == 200 and 'id' in result:
            logger.info(f"Facebook post created: {result['id']}")
            return {
                'success': True,
                'platform': 'facebook',
                'post_id': result['id'],
                'message': 'Posted to Facebook successfully'
            }
        else:
            logger.error(f"Facebook API error: {result}")
            return {'success': False, 'error': result.get('error', {}).get('message', 'Unknown error')}
    
    except Exception as e:
        logger.error(f"Facebook post failed: {str(e)}")
        return {'success': False, 'error': str(e)}


def post_to_instagram(caption, image_url=None, media_type='IMAGE'):
    """
    Post to Instagram Business Account.
    
    Args:
        caption: Post caption
        image_url: URL of the image to post
        media_type: IMAGE, CAROUSEL, VIDEO, REELS
    
    Returns:
        dict: Post result
    """
    if not INSTAGRAM_CONFIG['access_token'] or not INSTAGRAM_CONFIG['business_account_id']:
        return {'success': False, 'error': 'Instagram credentials not configured'}
    
    if not image_url:
        return {'success': False, 'error': 'image_url is required for Instagram posts'}
    
    try:
        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_CONFIG['business_account_id']}/media"
        
        container_params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': INSTAGRAM_CONFIG['access_token'],
            'media_type': media_type
        }
        
        response = requests.post(container_url, data=container_params, timeout=30)
        container_result = response.json()
        
        if response.status_code != 200 or 'id' not in container_result:
            logger.error(f"Instagram container creation error: {container_result}")
            return {'success': False, 'error': container_result.get('error', {}).get('message', 'Unknown error')}
        
        container_id = container_result['id']
        
        # Step 2: Publish the media
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_CONFIG['business_account_id']}/media_publish"
        
        publish_params = {
            'creation_id': container_id,
            'access_token': INSTAGRAM_CONFIG['access_token']
        }
        
        response = requests.post(publish_url, data=publish_params, timeout=30)
        publish_result = response.json()
        
        if response.status_code == 200 and 'id' in publish_result:
            logger.info(f"Instagram post created: {publish_result['id']}")
            return {
                'success': True,
                'platform': 'instagram',
                'post_id': publish_result['id'],
                'caption': caption
            }
        else:
            logger.error(f"Instagram publish error: {publish_result}")
            return {'success': False, 'error': publish_result.get('error', {}).get('message', 'Unknown error')}
    
    except Exception as e:
        logger.error(f"Instagram post failed: {str(e)}")
        return {'success': False, 'error': str(e)}


def post_to_twitter(text, media_urls=None):
    """
    Post to Twitter/X.
    
    Args:
        text: Tweet text (max 280 characters)
        media_urls: Optional list of media URLs
    
    Returns:
        dict: Post result
    """
    if not TWITTER_CONFIG['bearer_token']:
        return {'success': False, 'error': 'Twitter credentials not configured'}
    
    if len(text) > 280:
        return {'success': False, 'error': 'Tweet text must be 280 characters or less'}
    
    url = "https://api.twitter.com/2/tweets"
    
    headers = {
        'Authorization': f"Bearer {TWITTER_CONFIG['bearer_token']}",
        'Content-Type': 'application/json'
    }
    
    payload = {
        'text': text
    }
    
    # Note: Media upload requires additional steps (upload media first, then attach)
    # This is a simplified version
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if response.status_code == 201 and 'data' in result:
            logger.info(f"Twitter post created: {result['data']['id']}")
            return {
                'success': True,
                'platform': 'twitter',
                'post_id': result['data']['id'],
                'text': text
            }
        else:
            logger.error(f"Twitter API error: {result}")
            return {'success': False, 'error': result.get('errors', [{}])[0].get('message', 'Unknown error')}
    
    except Exception as e:
        logger.error(f"Twitter post failed: {str(e)}")
        return {'success': False, 'error': str(e)}


def post_to_linkedin(text, title=None, url=None):
    """
    Post to LinkedIn Company Page or Personal Profile.
    
    Args:
        text: Post text
        title: Optional title for shared content
        url: Optional URL to share
    
    Returns:
        dict: Post result
    """
    if not LINKEDIN_CONFIG['access_token']:
        return {'success': False, 'error': 'LinkedIn credentials not configured'}
    
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    headers = {
        'Authorization': f"Bearer {LINKEDIN_CONFIG['access_token']}",
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Determine if posting to organization or personal
    if LINKEDIN_CONFIG['organization_id']:
        author = f"urn:li:organization:{LINKEDIN_CONFIG['organization_id']}"
    else:
        author = "urn:li:person:YOUR_PERSON_URN"  # Would need to get from API
    
    payload = {
        'author': author,
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {
                    'text': text
                },
                'shareMediaCategory': 'NONE'
            }
        },
        'visibility': {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        }
    }
    
    if url:
        payload['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'ARTICLE'
        payload['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [{
            'status': 'READY',
            'description': {
                'text': title or text
            },
            'originalUrl': url,
            'title': {
                'text': title or 'Shared Link'
            }
        }]
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if response.status_code in [200, 201] and 'id' in result:
            post_id = result['id']
            logger.info(f"LinkedIn post created: {post_id}")
            return {
                'success': True,
                'platform': 'linkedin',
                'post_id': post_id,
                'text': text
            }
        else:
            logger.error(f"LinkedIn API error: {result}")
            return {'success': False, 'error': str(result)}
    
    except Exception as e:
        logger.error(f"LinkedIn post failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Social Media MCP Server',
        'version': '1.0.0',
        'platforms': {
            'facebook': bool(FACEBOOK_CONFIG['access_token']),
            'instagram': bool(INSTAGRAM_CONFIG['access_token']),
            'twitter': bool(TWITTER_CONFIG['bearer_token']),
            'linkedin': bool(LINKEDIN_CONFIG['access_token'])
        },
        'endpoints': [
            '/post',
            '/post/facebook',
            '/post/instagram',
            '/post/twitter',
            '/post/linkedin',
            '/analytics',
            '/schedule'
        ]
    })


@app.route('/post', methods=['POST'])
def post_to_all():
    """
    Post to all configured social media platforms.
    
    JSON body:
        - text: Post text (required)
        - platforms: List of platforms ['facebook', 'instagram', 'twitter', 'linkedin']
        - image_url: Optional image URL
        - link: Optional link to share
        - title: Optional title for link
    """
    try:
        data = request.get_json()
        
        text = data.get('text')
        if not text:
            return jsonify({'success': False, 'error': 'text is required'}), 400
        
        platforms = data.get('platforms', ['facebook', 'instagram', 'twitter', 'linkedin'])
        image_url = data.get('image_url')
        link = data.get('link')
        title = data.get('title')
        
        results = {
            'success': [],
            'failed': []
        }
        
        # Post to each platform
        if 'facebook' in platforms:
            result = post_to_facebook(text, link, image_url)
            if result.get('success'):
                results['success'].append(result)
            else:
                results['failed'].append({'platform': 'facebook', 'error': result.get('error')})
        
        if 'instagram' in platforms and image_url:
            result = post_to_instagram(text, image_url)
            if result.get('success'):
                results['success'].append(result)
            else:
                results['failed'].append({'platform': 'instagram', 'error': result.get('error')})
        
        if 'twitter' in platforms:
            result = post_to_twitter(text, [image_url] if image_url else None)
            if result.get('success'):
                results['success'].append(result)
            else:
                results['failed'].append({'platform': 'twitter', 'error': result.get('error')})
        
        if 'linkedin' in platforms:
            result = post_to_linkedin(text, title, link)
            if result.get('success'):
                results['success'].append(result)
            else:
                results['failed'].append({'platform': 'linkedin', 'error': result.get('error')})
        
        # Log the action
        log_social_post(results)
        
        return jsonify({
            'success': len(results['failed']) == 0,
            'posted_to': len(results['success']),
            'failed_on': len(results['failed']),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Error posting to social media: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/post/facebook', methods=['POST'])
def post_facebook():
    """Post to Facebook only"""
    try:
        data = request.get_json()
        text = data.get('message', data.get('text'))
        
        result = post_to_facebook(
            text,
            data.get('link'),
            data.get('photo_url', data.get('image_url'))
        )
        
        log_social_post({'success': [result] if result.get('success') else [], 
                        'failed': [] if result.get('success') else [{'platform': 'facebook', 'error': result.get('error')}]})
        
        return jsonify(result) if result.get('success') else jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/post/instagram', methods=['POST'])
def post_instagram():
    """Post to Instagram only"""
    try:
        data = request.get_json()
        
        result = post_to_instagram(
            data.get('caption', data.get('text')),
            data.get('image_url'),
            data.get('media_type', 'IMAGE')
        )
        
        log_social_post({'success': [result] if result.get('success') else [],
                        'failed': [] if result.get('success') else [{'platform': 'instagram', 'error': result.get('error')}]})
        
        return jsonify(result) if result.get('success') else jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/post/twitter', methods=['POST'])
def post_twitter():
    """Post to Twitter only"""
    try:
        data = request.get_json()
        
        result = post_to_twitter(
            data.get('text'),
            data.get('media_urls')
        )
        
        log_social_post({'success': [result] if result.get('success') else [],
                        'failed': [] if result.get('success') else [{'platform': 'twitter', 'error': result.get('error')}]})
        
        return jsonify(result) if result.get('success') else jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/post/linkedin', methods=['POST'])
def post_linkedin():
    """Post to LinkedIn only"""
    try:
        data = request.get_json()
        
        result = post_to_linkedin(
            data.get('text'),
            data.get('title'),
            data.get('url')
        )
        
        log_social_post({'success': [result] if result.get('success') else [],
                        'failed': [] if result.get('success') else [{'platform': 'linkedin', 'error': result.get('error')}]})
        
        return jsonify(result) if result.get('success') else jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Get analytics for social media posts.
    
    Query params:
        - platform: Filter by platform
        - days: Number of days to retrieve (default: 7)
    """
    try:
        platform = request.args.get('platform')
        days = int(request.args.get('days', 7))
        
        # Read analytics from vault
        analytics_dir = Path('vault/Social_Media_Analytics')
        analytics_dir.mkdir(exist_ok=True)
        
        analytics_file = analytics_dir / 'analytics_log.json'
        
        all_analytics = []
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                all_analytics = json.load(f)
        
        # Filter by date and platform
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = [
            a for a in all_analytics
            if datetime.fromisoformat(a['timestamp']) >= cutoff_date
            and (not platform or a.get('platform') == platform)
        ]
        
        # Aggregate stats
        stats = {
            'total_posts': len(filtered),
            'by_platform': {},
            'success_rate': 0
        }
        
        for post in filtered:
            platform_name = post.get('platform', 'unknown')
            if platform_name not in stats['by_platform']:
                stats['by_platform'][platform_name] = {'posts': 0, 'success': 0}
            stats['by_platform'][platform_name]['posts'] += 1
            if post.get('success'):
                stats['by_platform'][platform_name]['success'] += 1
        
        if stats['total_posts'] > 0:
            stats['success_rate'] = sum(p['success'] for p in stats['by_platform'].values()) / stats['total_posts'] * 100
        
        return jsonify({
            'success': True,
            'period_days': days,
            'stats': stats,
            'recent_posts': filtered[-10:]  # Last 10 posts
        })
    
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/schedule', methods=['POST'])
def schedule_post():
    """
    Schedule a social media post for later.
    
    JSON body:
        - text: Post text (required)
        - platforms: List of platforms
        - scheduled_time: ISO format datetime (required)
        - image_url: Optional image URL
        - link: Optional link
    """
    try:
        data = request.get_json()
        
        text = data.get('text')
        scheduled_time = data.get('scheduled_time')
        
        if not text or not scheduled_time:
            return jsonify({'success': False, 'error': 'text and scheduled_time are required'}), 400
        
        # Parse scheduled time
        try:
            schedule_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid scheduled_time format. Use ISO format'}), 400
        
        # Create scheduled post file
        scheduled_dir = Path('vault/Scheduled_Posts')
        scheduled_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        schedule_id = f"schedule_{timestamp}"
        
        scheduled_post = {
            'id': schedule_id,
            'text': text,
            'platforms': data.get('platforms', ['facebook', 'instagram', 'twitter', 'linkedin']),
            'scheduled_time': scheduled_time,
            'image_url': data.get('image_url'),
            'link': data.get('link'),
            'title': data.get('title'),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        # Save scheduled post
        schedule_file = scheduled_dir / f"{schedule_id}.json"
        with open(schedule_file, 'w') as f:
            json.dump(scheduled_post, f, indent=2)
        
        logger.info(f"Scheduled post created: {schedule_id} for {scheduled_time}")
        
        return jsonify({
            'success': True,
            'schedule_id': schedule_id,
            'scheduled_time': scheduled_time,
            'message': f'Post scheduled for {scheduled_time}'
        })
    
    except Exception as e:
        logger.error(f"Error scheduling post: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/schedule/<schedule_id>/cancel', methods=['POST'])
def cancel_schedule(schedule_id):
    """Cancel a scheduled post"""
    try:
        scheduled_dir = Path('vault/Scheduled_Posts')
        schedule_file = scheduled_dir / f"{schedule_id}.json"
        
        if not schedule_file.exists():
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        # Read and update status
        with open(schedule_file, 'r') as f:
            scheduled_post = json.load(f)
        
        scheduled_post['status'] = 'cancelled'
        
        with open(schedule_file, 'w') as f:
            json.dump(scheduled_post, f, indent=2)
        
        logger.info(f"Scheduled post cancelled: {schedule_id}")
        
        return jsonify({
            'success': True,
            'message': f'Schedule {schedule_id} cancelled'
        })
    
    except Exception as e:
        logger.error(f"Error cancelling schedule: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def log_social_post(results):
    """Log social media post to analytics file"""
    try:
        analytics_dir = Path('vault/Social_Media_Analytics')
        analytics_dir.mkdir(exist_ok=True)
        
        analytics_file = analytics_dir / 'analytics_log.json'
        
        all_analytics = []
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                all_analytics = json.load(f)
        
        # Log each result
        for post in results.get('success', []):
            all_analytics.append({
                'timestamp': datetime.now().isoformat(),
                'platform': post.get('platform'),
                'post_id': post.get('post_id'),
                'success': True
            })
        
        for post in results.get('failed', []):
            all_analytics.append({
                'timestamp': datetime.now().isoformat(),
                'platform': post.get('platform'),
                'success': False,
                'error': post.get('error')
            })
        
        with open(analytics_file, 'w') as f:
            json.dump(all_analytics, f, indent=2)
    
    except Exception as e:
        logger.error(f"Error logging social post: {str(e)}")


if __name__ == '__main__':
    logger.info("Starting Social Media MCP Server...")
    logger.info(f"Facebook configured: {bool(FACEBOOK_CONFIG['access_token'])}")
    logger.info(f"Instagram configured: {bool(INSTAGRAM_CONFIG['access_token'])}")
    logger.info(f"Twitter configured: {bool(TWITTER_CONFIG['bearer_token'])}")
    logger.info(f"LinkedIn configured: {bool(LINKEDIN_CONFIG['access_token'])}")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
