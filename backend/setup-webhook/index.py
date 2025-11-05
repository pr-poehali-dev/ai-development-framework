"""
Business: Setup Telegram bot webhook automatically
Args: event - HTTP request
      context - Cloud function context
Returns: Webhook setup status
"""

import json
import os
import requests
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': 'TELEGRAM_BOT_TOKEN not set'
            }),
            'isBase64Encoded': False
        }
    
    webhook_url = 'https://functions.poehali.dev/f6f61a49-4b63-4bdb-bf43-e48cc42a66c4'
    
    if method == 'GET':
        url = f'https://api.telegram.org/bot{bot_token}/getWebhookInfo'
        response = requests.get(url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response.json()),
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
        data = {
            'url': webhook_url,
            'allowed_updates': ['message']
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('ok'):
            bot_info_url = f'https://api.telegram.org/bot{bot_token}/getMe'
            bot_info = requests.get(bot_info_url).json()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'webhook_url': webhook_url,
                    'bot': bot_info.get('result', {})
                }),
                'isBase64Encoded': False
            }
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'error': result.get('description', 'Unknown error')
                }),
                'isBase64Encoded': False
            }
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }
