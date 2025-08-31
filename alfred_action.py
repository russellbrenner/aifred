#!/usr/bin/env python3

import json
import sqlite3
import sys
import os
import requests
from pathlib import Path
from aifred import AifredDB

class AIClient:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.claude_key = os.getenv('CLAUDE_API_KEY')
    
    def continue_chatgpt_conversation(self, messages, new_message):
        if not self.openai_key:
            return "Error: OpenAI API key not configured"
        
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        # Convert stored messages to OpenAI format
        conversation = []
        for msg in messages:
            if msg.get('author', {}).get('role') in ['user', 'assistant']:
                conversation.append({
                    'role': msg['author']['role'],
                    'content': msg.get('content', {}).get('parts', [''])[0]
                })
        
        # Add new message
        conversation.append({'role': 'user', 'content': new_message})
        
        data = {
            'model': 'gpt-4',
            'messages': conversation,
            'max_tokens': 1000
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"
    
    def continue_claude_conversation(self, messages, new_message):
        if not self.claude_key:
            return "Error: Claude API key not configured"
        
        headers = {
            'x-api-key': self.claude_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # Convert stored messages to Claude format
        conversation = []
        for msg in messages:
            if msg.get('sender') in ['human', 'assistant']:
                conversation.append({
                    'role': msg['sender'],
                    'content': msg.get('text', '')
                })
        
        # Add new message
        conversation.append({'role': 'human', 'content': new_message})
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 1000,
            'messages': conversation
        }
        
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()['content'][0]['text']
        except Exception as e:
            return f"Error: {str(e)}"

def handle_action(action_arg):
    db = AifredDB()
    ai_client = AIClient()
    
    if action_arg == "import":
        # Open file dialog for import (this would need AppleScript integration)
        print("Import feature - select your export file")
        return
    
    if action_arg.startswith("continue:"):
        conv_id = action_arg[9:]
        new_message = input("Enter your message: ")
        
        # Get conversation from DB
        conn = sqlite3.connect(db.db_path)
        cursor = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print("Conversation not found")
            return
        
        conv_id, title, platform, created_at, updated_at, messages_json, is_favourite, is_pinned = result
        messages = json.loads(messages_json)
        
        if platform == 'chatgpt':
            # Extract messages from ChatGPT mapping format
            message_list = []
            for msg_id, msg_data in messages.items():
                if msg_data.get('message'):
                    message_list.append(msg_data['message'])
            
            response = ai_client.continue_chatgpt_conversation(message_list, new_message)
        elif platform == 'claude':
            response = ai_client.continue_claude_conversation(messages, new_message)
        else:
            response = "Unsupported platform"
        
        print(f"AI Response:\n{response}")
        
        # Update conversation in DB with new exchange
        # (Implementation would store the new message and response)
    
    elif action_arg.startswith("fav:"):
        conv_id = action_arg[4:]
        conn = sqlite3.connect(db.db_path)
        conn.execute("UPDATE conversations SET is_favourite = NOT is_favourite WHERE id = ?", (conv_id,))
        conn.commit()
        conn.close()
        print("Toggled favourite status")
    
    elif action_arg.startswith("pin:"):
        conv_id = action_arg[4:]
        conn = sqlite3.connect(db.db_path)
        conn.execute("UPDATE conversations SET is_pinned = NOT is_pinned WHERE id = ?", (conv_id,))
        conn.commit()
        conn.close()
        print("Toggled pin status")
    
    elif action_arg.startswith("new:"):
        message = action_arg[4:]
        # Start new conversation with selected AI
        print(f"Starting new conversation: {message}")
        # This would typically open a chat interface or send to preferred AI

def main():
    if len(sys.argv) < 2:
        print("No action specified")
        return
    
    action_arg = sys.argv[1]
    handle_action(action_arg)

if __name__ == "__main__":
    main()