#!/usr/bin/env python3

import json
import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from store import Store

class AifredDB:
    def __init__(self):
        # Use Alfred's recommended data directory
        data_dir = os.getenv('alfred_workflow_data')
        if not data_dir:
            # Fallback to Alfred's standard data path
            data_dir = Path.home() / 'Library/Application Support/Alfred/Workflow Data/com.rbrenner.aifred'
        else:
            data_dir = Path(data_dir)
        
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / 'conversations.db'
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                platform TEXT,
                created_at TEXT,
                updated_at TEXT,
                messages TEXT,
                is_favourite INTEGER DEFAULT 0,
                is_pinned INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def import_chatgpt_export(self, export_path):
        try:
            print("⏳ Reading ChatGPT export file...")
            with open(export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Expected a list of conversations")
            
            print(f"📚 Processing {len(data)} conversations...")
            conn = sqlite3.connect(self.db_path)
            imported = 0
            
            for conversation in data:
                try:
                    conv_id = conversation.get('id', str(conversation.get('create_time', '')))
                    title = conversation.get('title', 'Untitled')
                    created_at = datetime.fromtimestamp(conversation.get('create_time', 0)).isoformat()
                    updated_at = datetime.fromtimestamp(conversation.get('update_time', 0)).isoformat()
                    messages = json.dumps(conversation.get('mapping', {}))
                    
                    conn.execute('''
                        INSERT OR REPLACE INTO conversations 
                        (id, title, platform, created_at, updated_at, messages)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (conv_id, title, 'chatgpt', created_at, updated_at, messages))
                    imported += 1
                    
                    if imported % 50 == 0:
                        print(f"⏳ Processed {imported} conversations...")
                        
                except Exception as e:
                    print(f"⚠️ Warning: Skipped conversation due to error: {e}")
                    continue
            
            conn.commit()
            conn.close()
            print(f"✅ Successfully imported {imported} ChatGPT conversations")
            return imported
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Export file not found: {export_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in export file: {e}")
        except Exception as e:
            raise Exception(f"Import failed: {e}")
    
    def import_claude_export(self, export_path):
        try:
            print("⏳ Reading Claude export file...")
            with open(export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Expected a list of conversations")
            
            print(f"📚 Processing {len(data)} conversations...")
            conn = sqlite3.connect(self.db_path)
            imported = 0
            
            for conversation in data:
                try:
                    conv_id = conversation.get('uuid', conversation.get('id', ''))
                    title = conversation.get('name', 'Untitled')
                    created_at = conversation.get('created_at', datetime.now().isoformat())
                    updated_at = conversation.get('updated_at', created_at)
                    messages = json.dumps(conversation.get('chat_messages', []))
                    
                    conn.execute('''
                        INSERT OR REPLACE INTO conversations 
                        (id, title, platform, created_at, updated_at, messages)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (conv_id, title, 'claude', created_at, updated_at, messages))
                    imported += 1
                    
                    if imported % 50 == 0:
                        print(f"⏳ Processed {imported} conversations...")
                        
                except Exception as e:
                    print(f"⚠️ Warning: Skipped conversation due to error: {e}")
                    continue
            
            conn.commit()
            conn.close()
            print(f"✅ Successfully imported {imported} Claude conversations")
            return imported
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Export file not found: {export_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in export file: {e}")
        except Exception as e:
            raise Exception(f"Import failed: {e}")
    
    def search_conversations(self, query="", platform=None, favourite=None, pinned=None):
        conn = sqlite3.connect(self.db_path)
        
        sql = "SELECT * FROM conversations WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR messages LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if platform:
            sql += " AND platform = ?"
            params.append(platform)
        
        if favourite is not None:
            sql += " AND is_favourite = ?"
            params.append(1 if favourite else 0)
        
        if pinned is not None:
            sql += " AND is_pinned = ?"
            params.append(1 if pinned else 0)
        
        sql += " ORDER BY updated_at DESC"
        
        cursor = conn.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python aifred.py <command> [args]")
        return
    
    command = sys.argv[1]
    db = AifredDB()
    
    if command == "import":
        if len(sys.argv) < 4:
            print("Usage: python aifred.py import <platform> <file_path>")
            return
        
        platform = sys.argv[2]
        file_path = sys.argv[3]
        
        if platform == "chatgpt":
            count = db.import_chatgpt_export(file_path)
            print(f"Imported {count} ChatGPT conversations")
        elif platform == "claude":
            count = db.import_claude_export(file_path)
            print(f"Imported {count} Claude conversations")
        else:
            print(f"Unsupported platform: {platform}")
    
    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = db.search_conversations(query)
        
        for row in results:
            print(f"{row[1]} ({row[2]}) - {row[4]}")

    elif command == "redact":
        if len(sys.argv) < 3:
            print("Usage: python aifred.py redact <thread_id> [--mask] [output_path]")
            return
        thread_id_s = sys.argv[2]
        mask = "--mask" in sys.argv
        output_path: Optional[str] = None
        for arg in sys.argv[3:]:
            if arg != "--mask":
                output_path = arg
                break

        try:
            thread_id = int(thread_id_s)
        except ValueError:
            print("thread_id must be an integer")
            return

        store = Store()
        thread = store.get_thread(thread_id)
        if not thread:
            print("Thread not found")
            return
        messages = store.get_thread_messages(thread.id)

        def _redact_text(t: str) -> str:
            if not mask:
                return t
            # Basic mask: keep first/last 10 chars
            return (t[:10] + "…" + t[-10:]) if len(t) > 25 else "[…redacted…]"

        export = {
            "thread": {
                "id": thread.id,
                "provider": thread.provider,
                "model": thread.model,
                "name": thread.name,
                "created_at": thread.created_at,
                "updated_at": thread.updated_at,
            },
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": _redact_text(m.content),
                    "meta": m.meta,
                    "created_at": m.created_at,
                }
                for m in messages
            ],
        }

        data = json.dumps(export, ensure_ascii=False, indent=2)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(data)
            print(f"Exported redacted thread to {output_path}")
        else:
            print(data)

if __name__ == "__main__":
    main()
