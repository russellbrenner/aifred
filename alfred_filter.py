#!/usr/bin/env python3

import json
import sys
from aifred import AifredDB

def alfred_items(items):
    """Format items for Alfred Script Filter output"""
    return json.dumps({"items": items})

def search_conversations(query):
    db = AifredDB()
    
    # Parse query for filters
    platform_filter = None
    favourite_filter = None
    pinned_filter = None
    search_query = query
    
    # Handle bang filters
    if "!chatgpt" in query:
        platform_filter = "chatgpt"
        search_query = query.replace("!chatgpt", "").strip()
    elif "!claude" in query:
        platform_filter = "claude"
        search_query = query.replace("!claude", "").strip()
    
    if "!fav" in query or "!favourite" in query:
        favourite_filter = True
        search_query = search_query.replace("!fav", "").replace("!favourite", "").strip()
    
    if "!pin" in query or "!pinned" in query:
        pinned_filter = True
        search_query = search_query.replace("!pin", "").replace("!pinned", "").strip()
    
    results = db.search_conversations(
        query=search_query,
        platform=platform_filter,
        favourite=favourite_filter,
        pinned=pinned_filter
    )
    
    items = []
    
    # Add import option if no results and query contains 'import'
    if not results and 'import' in query.lower():
        items.append({
            "uid": "import",
            "title": "Import Conversations",
            "subtitle": "Import ChatGPT or Claude conversation exports",
            "arg": "import",
            "icon": {"type": "default", "path": "icon.png"}
        })
    
    # Add conversation results
    for row in results[:20]:  # Limit to 20 results
        conv_id, title, platform, created_at, updated_at, messages, is_favourite, is_pinned = row
        
        subtitle = f"{platform.title()} • {updated_at[:10]}"
        if is_favourite:
            subtitle += " ⭐"
        if is_pinned:
            subtitle += " 📌"
        
        items.append({
            "uid": conv_id,
            "title": title,
            "subtitle": subtitle,
            "arg": conv_id,
            "icon": {"type": "default", "path": f"{platform}_icon.png"},
            "mods": {
                "alt": {
                    "subtitle": "Continue this conversation",
                    "arg": f"continue:{conv_id}"
                },
                "cmd": {
                    "subtitle": "Toggle favourite",
                    "arg": f"fav:{conv_id}"
                },
                "ctrl": {
                    "subtitle": "Toggle pin",
                    "arg": f"pin:{conv_id}"
                }
            }
        })
    
    # Add new conversation option
    if query and not query.startswith('!'):
        items.insert(0, {
            "uid": "new",
            "title": f"New conversation: {query}",
            "subtitle": "Start a new AI conversation",
            "arg": f"new:{query}",
            "icon": {"type": "default", "path": "new_icon.png"}
        })
    
    return alfred_items(items)

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    print(search_conversations(query))

if __name__ == "__main__":
    main()