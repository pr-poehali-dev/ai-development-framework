"""
Business: Telegram bot webhook handler with AI capabilities
Args: event - HTTP event with Telegram webhook data
      context - Cloud function context
Returns: HTTP response for Telegram webhook
"""

import json
import os
import psycopg2
import requests
import re
from typing import Dict, Any, Optional
from datetime import datetime
from difflib import SequenceMatcher

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

HARMFUL_PATTERNS = [
    r'\b(убий|убить|смерть|насилие|терроризм)\b',
    r'\b(наркотик|кокаин|героин|мет)\b',
    r'\b(порн|секс|xxx|эротик)\b',
    r'\b(нацис|фашис|расизм|геноцид)\b',
]

def is_safe_content(text: str) -> bool:
    """Проверка контента на безопасность"""
    text_lower = text.lower()
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    return True

def fuzzy_match(text: str, target: str, threshold: float = 0.75) -> bool:
    """Нечеткое сравнение строк для распознавания опечаток"""
    return SequenceMatcher(None, text.lower(), target.lower()).ratio() > threshold

def is_bot_mentioned(text: str, chat_type: str) -> bool:
    """Проверка упоминания бота в группе"""
    if chat_type == 'private':
        return True
    
    text_lower = text.lower()
    keywords = ['nonillionai', 'нониллион', 'нонилион', 'nonillion']
    
    for keyword in keywords:
        if keyword in text_lower:
            return True
        for word in text_lower.split():
            if fuzzy_match(word, keyword, 0.7):
                return True
    
    return False

def generate_ai_response(user_message: str, history: list, user_name: str = '') -> str:
    """Генерация ответа ИИ на основе контекста"""
    message_lower = user_message.lower()
    
    if not is_safe_content(user_message):
        return '❌ Извините, я не могу обработать такой запрос. Давайте обсудим что-то позитивное!'
    
    if 'кто ты' in message_lower or 'представься' in message_lower:
        return '👋 Привет! Я **NonillionAI** — искусственный интеллект, созданный cat (@whimsical_cat). Я умею генерировать изображения, отвечать на вопросы и помогать с творческими задачами!'
    
    if 'привет' in message_lower or 'start' in message_lower or 'здравствуй' in message_lower:
        return f'Привет, {user_name}! 👋 Я **NonillionAI**, созданный cat (@whimsical_cat). Умею генерировать изображения по описанию! Просто скажи "нарисуй" и опиши, что хочешь увидеть.'
    
    if 'нарисуй' in message_lower or 'изображение' in message_lower or 'картинк' in message_lower or 'сгенерируй' in message_lower:
        prompt = re.sub(r'(нарисуй|изображение|картинку|сгенерируй)', '', message_lower, flags=re.IGNORECASE).strip()
        if len(prompt) < 3:
            return '🎨 Опишите, что вы хотите увидеть на изображении! Например: "нарисуй закат над океаном"'
        return 'generate_image'
    
    if 'спасибо' in message_lower or 'благодарю' in message_lower:
        return 'Рад помочь! 😊 Обращайтесь, если нужна еще помощь!'
    
    return 'Я **NonillionAI**, созданный cat (@whimsical_cat). Умею генерировать изображения — просто напишите "нарисуй" и опишите что хотите!'

def send_telegram_message(chat_id: int, text: str, photo_url: str = None) -> None:
    """Отправить сообщение в Telegram"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return
    
    if photo_url:
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        data = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': text
        }
    else:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text
        }
    
    requests.post(url, json=data)

def generate_image(prompt: str, user_id: int, conversation_id: int, chat_id: int) -> Optional[str]:
    """Генерация изображения через FLUX"""
    if not is_safe_content(prompt):
        send_telegram_message(chat_id, '❌ Извините, не могу сгенерировать такое изображение.')
        return None
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id FROM generated_images 
        WHERE user_id = %s AND prompt = %s AND status = 'processing'
        AND created_at > NOW() - INTERVAL '1 minute'
    """, (user_id, prompt))
    
    existing = cur.fetchone()
    if existing:
        cur.close()
        conn.close()
        return None
    
    cur.execute("""
        INSERT INTO generated_images (user_id, conversation_id, prompt, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (user_id, conversation_id, prompt, 'processing', datetime.now()))
    
    image_id = cur.fetchone()[0]
    conn.commit()
    
    try:
        flux_api_key = os.environ.get('FLUX_API_KEY')
        if not flux_api_key:
            image_url = f'https://via.placeholder.com/1024x1024.png?text=Image+{image_id}'
        else:
            response = requests.post(
                'https://api.flux.ai/v1/generate',
                json={'prompt': prompt, 'width': 1024, 'height': 1024},
                headers={'Authorization': f'Bearer {flux_api_key}'},
                timeout=30
            )
            if response.status_code == 200:
                image_url = response.json().get('url')
            else:
                image_url = f'https://via.placeholder.com/1024x1024.png?text=Error'
        
        cur.execute("""
            UPDATE generated_images 
            SET status = %s, image_url = %s, completed_at = %s
            WHERE id = %s
        """, ('completed', image_url, datetime.now(), image_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return image_url
    except Exception as e:
        cur.execute("""
            UPDATE generated_images 
            SET status = %s, error_message = %s
            WHERE id = %s
        """, ('failed', str(e), image_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return None

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
        chat_type = chat.get('type', 'private')
        chat_id = chat.get('id')
        
        if not user or not text:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True}),
                'isBase64Encoded': False
            }
        
        if not is_bot_mentioned(text, chat_type):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True}),
                'isBase64Encoded': False
            }
        
        telegram_id = user.get('id')
        user_name = user.get('first_name', 'друг')
        
        save_user(user)
        
        conversation_id = get_or_create_conversation(telegram_id)
        
        save_message(conversation_id, telegram_id, 'user', text)
        
        history = get_conversation_history(conversation_id)
        
        ai_response = generate_ai_response(text, history, user_name)
        
        if ai_response == 'generate_image':
            prompt = re.sub(r'(нарисуй|изображение|картинку|сгенерируй|nonillionai|нониллион)', '', text, flags=re.IGNORECASE).strip()
            
            if len(prompt) < 3:
                send_telegram_message(chat_id, '🎨 Опишите, что вы хотите увидеть на изображении!')
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'ok': True}),
                    'isBase64Encoded': False
                }
            
            send_telegram_message(chat_id, '🎨 Генерирую изображение, подождите немного...')
            
            image_url = generate_image(prompt, telegram_id, conversation_id, chat_id)
            
            if image_url:
                send_telegram_message(chat_id, f'✅ Готово! Вот изображение: "{prompt}"', image_url)
                save_message(conversation_id, telegram_id, 'assistant', f'[Изображение: {prompt}]')
            else:
                save_message(conversation_id, telegram_id, 'assistant', '[Ошибка генерации]')
        else:
            send_telegram_message(chat_id, ai_response)
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
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }