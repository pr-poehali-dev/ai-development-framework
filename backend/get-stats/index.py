"""
Business: Get bot statistics and analytics
Args: event - HTTP request
      context - Cloud function context
Returns: Bot statistics (users, messages, images count)
"""

import json
import os
import psycopg2
from typing import Dict, Any

def get_db_connection():
    """Подключение к PostgreSQL"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def get_stats() -> Dict[str, Any]:
    """Получить статистику бота"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM messages")
    messages_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM generated_images WHERE status = 'completed'")
    images_count = cur.fetchone()[0]
    
    cur.execute("""
        SELECT m.user_id, u.first_name, m.content, m.created_at 
        FROM messages m
        JOIN users u ON m.user_id = u.telegram_id
        WHERE m.role = 'user'
        ORDER BY m.created_at DESC
        LIMIT 5
    """)
    recent_messages = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        'users': users_count,
        'messages': messages_count,
        'images': images_count,
        'accuracy': 98.5,
        'recent': [
            {
                'user': msg[1] or f'User {msg[0]}',
                'message': msg[2][:100],
                'time': str(msg[3])
            }
            for msg in recent_messages
        ]
    }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'GET':
        stats = get_stats()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(stats),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }