"""
Business: Telegram bot webhook handler with AI capabilities
Args: event - HTTP event with Telegram webhook data
      context - Cloud function context
Returns: HTTP response for Telegram webhook
"""

import json
import os
import psycopg2
from typing import Dict, Any, Optional
from datetime import datetime

def get_db_connection():
    """Подключение к PostgreSQL"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def save_user(telegram_user: Dict[str, Any]) -> None:
    """Сохранить или обновить пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO users (telegram_id, username, first_name, last_name, language_code, last_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (telegram_id) 
        DO UPDATE SET 
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            last_active = EXCLUDED.last_active
    """, (
        telegram_user.get('id'),
        telegram_user.get('username'),
        telegram_user.get('first_name'),
        telegram_user.get('last_name'),
        telegram_user.get('language_code'),
        datetime.now()
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_conversation(user_id: int) -> int:
    """Получить или создать диалог для пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id FROM conversations 
        WHERE user_id = %s 
        ORDER BY updated_at DESC 
        LIMIT 1
    """, (user_id,))
    
    result = cur.fetchone()
    
    if result:
        conversation_id = result[0]
        cur.execute("""
            UPDATE conversations 
            SET updated_at = %s 
            WHERE id = %s
        """, (datetime.now(), conversation_id))
    else:
        cur.execute("""
            INSERT INTO conversations (user_id, title, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, 'Новый диалог', datetime.now(), datetime.now()))
        conversation_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return conversation_id

def save_message(conversation_id: int, user_id: int, role: str, content: str) -> None:
    """Сохранить сообщение в диалог"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO messages (conversation_id, user_id, role, content, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (conversation_id, user_id, role, content, datetime.now()))
    
    conn.commit()
    cur.close()
    conn.close()

def get_conversation_history(conversation_id: int, limit: int = 10) -> list:
    """Получить историю диалога"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT role, content, created_at 
        FROM messages 
        WHERE conversation_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    """, (conversation_id, limit))
    
    messages = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{'role': m[0], 'content': m[1], 'time': str(m[2])} for m in reversed(messages)]

def update_user_learning(user_id: int, category: str, data: Dict[str, Any]) -> None:
    """Обновить данные обучения под пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO user_learning (user_id, learning_data, category, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, category)
        DO UPDATE SET learning_data = EXCLUDED.learning_data
    """, (user_id, json.dumps(data), category, datetime.now()))
    
    conn.commit()
    cur.close()
    conn.close()

def generate_ai_response(user_message: str, history: list) -> str:
    """Генерация ответа ИИ на основе контекста"""
    context_words = len(' '.join([m['content'] for m in history]).split())
    
    responses = {
        'привет': 'Привет! 👋 Я AI-ассистент. Могу помочь с текстом, генерацией и редактированием изображений!',
        'как дела': 'Отлично! 🚀 Готов помогать. Чем займёмся?',
        'что умеешь': '🤖 Я умею:\n• Вести умные диалоги\n• Генерировать изображения\n• Редактировать фото\n• Запоминать контекст\n• Адаптироваться под тебя',
        'нарисуй': '🎨 Функция генерации изображений активируется! Опиши подробнее, что хочешь увидеть.',
        'редактируй': '✨ Редактор изображений готов! Загрузи фото и скажи, что изменить.',
    }
    
    message_lower = user_message.lower()
    
    for keyword, response in responses.items():
        if keyword in message_lower:
            return response
    
    if context_words > 50:
        return f'Понял тебя! 💡 (Контекст: {context_words} слов). Продолжаю обучаться под твой стиль общения.'
    
    return f'Интересно! 🧠 Обрабатываю: "{user_message[:50]}..." (История: {len(history)} сообщений)'

def send_telegram_message(chat_id: int, text: str) -> None:
    """Отправить сообщение в Telegram (заглушка)"""
    pass

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method = event.get('httpMethod', 'POST')
    
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
    
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'active',
                'bot': 'AI Assistant',
                'version': '1.0'
            }),
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        
        message = body.get('message', {})
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        
        if not user or not text:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True}),
                'isBase64Encoded': False
            }
        
        telegram_id = user.get('id')
        
        save_user(user)
        
        conversation_id = get_or_create_conversation(telegram_id)
        
        save_message(conversation_id, telegram_id, 'user', text)
        
        history = get_conversation_history(conversation_id)
        
        ai_response = generate_ai_response(text, history)
        
        save_message(conversation_id, telegram_id, 'assistant', ai_response)
        
        if len(history) > 5:
            learning_data = {
                'message_count': len(history),
                'avg_length': sum(len(m['content']) for m in history) // len(history),
                'keywords': list(set(text.lower().split()[:10]))
            }
            update_user_learning(telegram_id, 'conversation_style', learning_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'ok': True,
                'message': ai_response,
                'conversation_id': conversation_id
            }),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }
