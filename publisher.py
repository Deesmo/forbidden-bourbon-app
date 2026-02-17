"""
Social Media Publisher Module
Handles API integrations for each platform.
Each publisher follows the same interface: publish(content, image_path, platform_config) -> result dict
"""

import requests
import json
import base64
import hashlib
import hmac
import time
import os
from urllib.parse import quote, urlencode
from datetime import datetime


class PublishResult:
    def __init__(self, success, platform, post_id='', url='', error=''):
        self.success = success
        self.platform = platform
        self.post_id = post_id
        self.url = url
        self.error = error
    
    def to_dict(self):
        return {
            'success': self.success,
            'platform': self.platform,
            'post_id': self.post_id,
            'url': self.url,
            'error': self.error
        }


# ============================================================
# BLUESKY PUBLISHER
# ============================================================

class BlueskyPublisher:
    """
    Bluesky AT Protocol publisher.
    Requires: handle (e.g. forbidden.bsky.social) and app password.
    Get an app password at: https://bsky.app/settings/app-passwords
    """
    
    BASE_URL = 'https://bsky.social/xrpc'
    
    @staticmethod
    def authenticate(handle, app_password):
        """Create a session and return access tokens"""
        try:
            resp = requests.post(f'{BlueskyPublisher.BASE_URL}/com.atproto.server.createSession', json={
                'identifier': handle,
                'password': app_password
            })
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'success': True,
                    'did': data['did'],
                    'access_jwt': data['accessJwt'],
                    'refresh_jwt': data['refreshJwt'],
                    'handle': data['handle']
                }
            else:
                return {'success': False, 'error': resp.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def upload_image(access_jwt, image_path):
        """Upload an image blob to Bluesky"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Determine mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'}
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            resp = requests.post(
                f'{BlueskyPublisher.BASE_URL}/com.atproto.repo.uploadBlob',
                headers={
                    'Authorization': f'Bearer {access_jwt}',
                    'Content-Type': mime_type
                },
                data=image_data
            )
            
            if resp.status_code == 200:
                return {'success': True, 'blob': resp.json()['blob']}
            else:
                return {'success': False, 'error': resp.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def publish(content, image_path='', config=None):
        """Publish a post to Bluesky"""
        if not config:
            return PublishResult(False, 'bluesky', error='No Bluesky configuration provided')
        
        handle = config.get('username', '')
        app_password = config.get('api_key', '')
        
        if not handle or not app_password:
            return PublishResult(False, 'bluesky', error='Bluesky handle and app password required')
        
        try:
            # Authenticate
            auth = BlueskyPublisher.authenticate(handle, app_password)
            if not auth['success']:
                return PublishResult(False, 'bluesky', error=f"Auth failed: {auth['error']}")
            
            # Build the post record
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            record = {
                'text': content,
                'createdAt': now,
                '$type': 'app.bsky.feed.post'
            }
            
            # Parse facets (links, mentions, hashtags)
            facets = BlueskyPublisher._parse_facets(content)
            if facets:
                record['facets'] = facets
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                img_result = BlueskyPublisher.upload_image(auth['access_jwt'], image_path)
                if img_result['success']:
                    record['embed'] = {
                        '$type': 'app.bsky.embed.images',
                        'images': [{
                            'alt': 'Forbidden Bourbon',
                            'image': img_result['blob']
                        }]
                    }
            
            # Create the post
            resp = requests.post(
                f'{BlueskyPublisher.BASE_URL}/com.atproto.repo.createRecord',
                headers={'Authorization': f'Bearer {auth["access_jwt"]}'},
                json={
                    'repo': auth['did'],
                    'collection': 'app.bsky.feed.post',
                    'record': record
                }
            )
            
            if resp.status_code == 200:
                data = resp.json()
                post_uri = data.get('uri', '')
                # Build a web URL from the URI
                rkey = post_uri.split('/')[-1] if '/' in post_uri else ''
                web_url = f"https://bsky.app/profile/{auth['handle']}/post/{rkey}"
                return PublishResult(True, 'bluesky', post_id=post_uri, url=web_url)
            else:
                return PublishResult(False, 'bluesky', error=resp.text)
                
        except Exception as e:
            return PublishResult(False, 'bluesky', error=str(e))
    
    @staticmethod
    def _parse_facets(text):
        """Parse URLs, mentions, and hashtags into Bluesky facets"""
        import re
        facets = []
        
        # URL detection
        url_pattern = re.compile(r'https?://[^\s<>\"\']+')
        for match in url_pattern.finditer(text):
            start = len(text[:match.start()].encode('utf-8'))
            end = len(text[:match.end()].encode('utf-8'))
            facets.append({
                'index': {'byteStart': start, 'byteEnd': end},
                'features': [{'$type': 'app.bsky.richtext.facet#link', 'uri': match.group()}]
            })
        
        # Hashtag detection
        hashtag_pattern = re.compile(r'(?:^|\s)(#[a-zA-Z0-9_]+)')
        for match in hashtag_pattern.finditer(text):
            tag = match.group(1)
            tag_start = match.start(1)
            start = len(text[:tag_start].encode('utf-8'))
            end = len(text[:tag_start + len(tag)].encode('utf-8'))
            facets.append({
                'index': {'byteStart': start, 'byteEnd': end},
                'features': [{'$type': 'app.bsky.richtext.facet#tag', 'tag': tag[1:]}]
            })
        
        return facets


# ============================================================
# TWITTER/X PUBLISHER (OAuth 2.0 with PKCE)
# ============================================================

class TwitterPublisher:
    """
    Twitter/X API v2 publisher.
    Requires: API Key, API Secret, Access Token, Access Token Secret.
    Get credentials at: https://developer.twitter.com/en/portal/dashboard
    You need a Free or Basic plan ($100/mo for Basic, Free allows 1,500 tweets/mo reading).
    Free tier: POST tweets only (perfect for us).
    """
    
    API_URL = 'https://api.twitter.com/2'
    UPLOAD_URL = 'https://upload.twitter.com/1.1'
    
    @staticmethod
    def _oauth1_header(method, url, params, api_key, api_secret, access_token, token_secret):
        """Generate OAuth 1.0a header"""
        import uuid
        
        oauth_params = {
            'oauth_consumer_key': api_key,
            'oauth_nonce': uuid.uuid4().hex,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': access_token,
            'oauth_version': '1.0'
        }
        
        all_params = {**oauth_params, **params}
        sorted_params = sorted(all_params.items())
        param_string = '&'.join(f'{quote(k, safe="")}={quote(str(v), safe="")}' for k, v in sorted_params)
        
        base_string = f'{method}&{quote(url, safe="")}&{quote(param_string, safe="")}'
        signing_key = f'{quote(api_secret, safe="")}&{quote(token_secret, safe="")}'
        
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()
        
        oauth_params['oauth_signature'] = signature
        auth_header = 'OAuth ' + ', '.join(
            f'{quote(k, safe="")}="{quote(v, safe="")}"' for k, v in sorted(oauth_params.items())
        )
        
        return auth_header
    
    @staticmethod
    def publish(content, image_path='', config=None):
        """Publish a tweet"""
        if not config:
            return PublishResult(False, 'twitter', error='No Twitter configuration provided')
        
        api_key = config.get('api_key', '')
        api_secret = config.get('api_secret', '')
        access_token = config.get('access_token', '')
        token_secret = config.get('refresh_token', '')  # We store token secret in refresh_token field
        
        if not all([api_key, api_secret, access_token, token_secret]):
            return PublishResult(False, 'twitter', error='Twitter API credentials incomplete')
        
        try:
            tweet_data = {'text': content}
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                # Upload media via v1.1 endpoint
                upload_url = f'{TwitterPublisher.UPLOAD_URL}/media/upload.json'
                
                with open(image_path, 'rb') as f:
                    files = {'media': f}
                    auth_header = TwitterPublisher._oauth1_header(
                        'POST', upload_url, {}, api_key, api_secret, access_token, token_secret
                    )
                    resp = requests.post(upload_url, headers={'Authorization': auth_header}, files=files)
                
                if resp.status_code == 200:
                    media_id = resp.json()['media_id_string']
                    tweet_data['media'] = {'media_ids': [media_id]}
            
            # Post the tweet
            tweet_url = f'{TwitterPublisher.API_URL}/tweets'
            auth_header = TwitterPublisher._oauth1_header(
                'POST', tweet_url, {}, api_key, api_secret, access_token, token_secret
            )
            
            resp = requests.post(
                tweet_url,
                headers={
                    'Authorization': auth_header,
                    'Content-Type': 'application/json'
                },
                json=tweet_data
            )
            
            if resp.status_code in [200, 201]:
                data = resp.json()
                tweet_id = data['data']['id']
                username = config.get('username', '')
                tweet_url = f'https://twitter.com/{username}/status/{tweet_id}' if username else ''
                return PublishResult(True, 'twitter', post_id=tweet_id, url=tweet_url)
            else:
                return PublishResult(False, 'twitter', error=f"HTTP {resp.status_code}: {resp.text}")
                
        except Exception as e:
            return PublishResult(False, 'twitter', error=str(e))


# ============================================================
# FACEBOOK PAGE PUBLISHER
# ============================================================

class FacebookPublisher:
    """
    Facebook Page publisher using Graph API.
    Requires: Page Access Token (long-lived).
    Get it at: https://developers.facebook.com/tools/explorer/
    You need a Facebook App and Page, then generate a Page Access Token.
    """
    
    GRAPH_URL = 'https://graph.facebook.com/v19.0'
    
    @staticmethod
    def publish(content, image_path='', config=None):
        """Publish a post to a Facebook Page"""
        if not config:
            return PublishResult(False, 'facebook', error='No Facebook configuration provided')
        
        access_token = config.get('access_token', '')
        page_id = config.get('username', '')  # We store page ID in username field
        
        if not access_token or not page_id:
            return PublishResult(False, 'facebook', error='Facebook Page ID and Access Token required')
        
        try:
            if image_path and os.path.exists(image_path):
                # Post with photo
                url = f'{FacebookPublisher.GRAPH_URL}/{page_id}/photos'
                with open(image_path, 'rb') as f:
                    resp = requests.post(url, data={
                        'caption': content,
                        'access_token': access_token
                    }, files={'source': f})
            else:
                # Text-only post
                url = f'{FacebookPublisher.GRAPH_URL}/{page_id}/feed'
                resp = requests.post(url, data={
                    'message': content,
                    'access_token': access_token
                })
            
            if resp.status_code == 200:
                data = resp.json()
                post_id = data.get('id', data.get('post_id', ''))
                post_url = f'https://facebook.com/{post_id}' if post_id else ''
                return PublishResult(True, 'facebook', post_id=post_id, url=post_url)
            else:
                return PublishResult(False, 'facebook', error=f"HTTP {resp.status_code}: {resp.text}")
                
        except Exception as e:
            return PublishResult(False, 'facebook', error=str(e))


# ============================================================
# LINKEDIN PUBLISHER
# ============================================================

class LinkedInPublisher:
    """
    LinkedIn Organization/Personal publisher.
    Requires: Access Token with w_member_social or w_organization_social scope.
    """
    
    API_URL = 'https://api.linkedin.com/v2'
    
    @staticmethod
    def publish(content, image_path='', config=None):
        """Publish a post to LinkedIn"""
        if not config:
            return PublishResult(False, 'linkedin', error='No LinkedIn configuration provided')
        
        access_token = config.get('access_token', '')
        author_urn = config.get('username', '')  # Format: urn:li:person:XXXX or urn:li:organization:XXXX
        
        if not access_token or not author_urn:
            return PublishResult(False, 'linkedin', error='LinkedIn Access Token and Author URN required')
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            post_data = {
                'author': author_urn,
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {'text': content},
                        'shareMediaCategory': 'NONE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            # Image upload for LinkedIn is more complex - skip for initial version
            # TODO: Implement LinkedIn image upload via registerUpload + upload flow
            
            resp = requests.post(
                f'{LinkedInPublisher.API_URL}/ugcPosts',
                headers=headers,
                json=post_data
            )
            
            if resp.status_code in [200, 201]:
                data = resp.json()
                post_id = data.get('id', '')
                return PublishResult(True, 'linkedin', post_id=post_id)
            else:
                return PublishResult(False, 'linkedin', error=f"HTTP {resp.status_code}: {resp.text}")
                
        except Exception as e:
            return PublishResult(False, 'linkedin', error=str(e))


# ============================================================
# PUBLISHER DISPATCHER
# ============================================================

PUBLISHERS = {
    'twitter': TwitterPublisher,
    'bluesky': BlueskyPublisher,
    'facebook': FacebookPublisher,
    'linkedin': LinkedInPublisher,
}

def publish_to_platform(platform_name, content, image_path='', config=None):
    """Dispatch to the appropriate publisher"""
    publisher = PUBLISHERS.get(platform_name)
    if not publisher:
        return PublishResult(False, platform_name, error=f'Unknown platform: {platform_name}')
    
    return publisher.publish(content, image_path, config)

def publish_to_all(content, image_path='', platforms_config=None):
    """Publish to all specified platforms and return results"""
    if not platforms_config:
        return []
    
    results = []
    for platform_name, config in platforms_config.items():
        result = publish_to_platform(platform_name, content, image_path, config)
        results.append(result.to_dict())
    
    return results
