import json
import os
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import typing

def parse_iso_datetime(dt_str: str) -> datetime:
    """Parses ISO 8601 strings safely."""
    # Remove 'Z' if present, replace with +00:00 or handle it
    if dt_str.endswith('Z'):
        dt_str = dt_str[:-1] + '+00:00'
    try:
        return datetime.fromisoformat(dt_str).replace(tzinfo=None)
    except ValueError:
        return datetime.min # fallback

def calculate_tokens(tmp_dir: Path, since: datetime = None, until: datetime = None) -> dict:
    """
    Main parser function that goes through the Gemini tmp directory, reads all JSON/JSONL
    chat files, applies date filters, and builds the aggregate stats.
    """
    stats = {
        'total_processed': 0,
        'input': 0,
        'output': 0,
        'cached': 0,
        'thoughts': 0,
        'total_turns': 0,
        'total_sessions': 0,
        'models': defaultdict(int),
        'projects': defaultdict(lambda: {'total': 0, 'input': 0, 'output': 0}),
        'top_sessions': [] # List of tuples: (tokens, session_id, project_alias, date)
    }

    # Use glob to find all json/jsonl files in chats folders
    search_pattern = os.path.join(str(tmp_dir), '*', 'chats', '**', '*.json*')
    chat_files = glob.glob(search_pattern, recursive=True)

    session_tracker = defaultdict(lambda: {'tokens': 0, 'project_alias': 'unknown', 'last_updated': datetime.min})

    for file_path in chat_files:
        path_parts = Path(file_path).parts
        # The alias/hash is usually two levels up from 'chats' 
        # C:/.../.gemini/tmp/<alias>/chats/...
        try:
            chats_index = path_parts.index('chats')
            project_alias = path_parts[chats_index - 1]
        except ValueError:
            project_alias = 'unknown'

        file_has_turns = False
        file_tokens = 0
        
        is_jsonl = file_path.endswith('.jsonl')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if is_jsonl:
                    for line in f:
                        try:
                            data = json.loads(line)
                            
                            # Filter by date if present on the line (e.g. $set: lastUpdated)
                            # or timestamp on individual messages
                            msg_time_str = data.get('timestamp') or data.get('lastUpdated')
                            msg_time = parse_iso_datetime(msg_time_str) if msg_time_str else None
                            
                            if msg_time:
                                if since and msg_time.replace(tzinfo=None) < since:
                                    continue
                                if until and msg_time.replace(tzinfo=None) > until:
                                    continue

                            tokens = data.get('tokens')
                            if tokens:
                                stats['input'] += tokens.get('input', 0)
                                stats['output'] += tokens.get('output', 0)
                                stats['cached'] += tokens.get('cached', 0)
                                stats['thoughts'] += tokens.get('thoughts', 0)
                                stats['total_processed'] += tokens.get('total', 0)
                                stats['total_turns'] += 1
                                
                                model = data.get('model', 'unknown')
                                stats['models'][model] += tokens.get('total', 0)
                                
                                stats['projects'][project_alias]['total'] += tokens.get('total', 0)
                                stats['projects'][project_alias]['input'] += tokens.get('input', 0)
                                stats['projects'][project_alias]['output'] += tokens.get('output', 0)
                                
                                file_tokens += tokens.get('total', 0)
                                file_has_turns = True
                                
                                session_id = data.get('sessionId') or data.get('id', 'unknown_session')
                                session_tracker[session_id]['tokens'] += tokens.get('total', 0)
                                session_tracker[session_id]['project_alias'] = project_alias
                                if msg_time and session_tracker[session_id]['last_updated'] < msg_time:
                                    session_tracker[session_id]['last_updated'] = msg_time
                        except json.JSONDecodeError:
                            continue
                else:
                    data = json.load(f)
                    
                    # Handle both list formats (like logs.json) and standard session dicts
                    messages = data if isinstance(data, list) else data.get('messages', [])
                    for msg in messages:
                        if not isinstance(msg, dict): continue
                        
                        msg_time_str = msg.get('timestamp')
                        msg_time = parse_iso_datetime(msg_time_str) if msg_time_str else None
                        
                        if msg_time:
                            if since and msg_time.replace(tzinfo=None) < since:
                                continue
                            if until and msg_time.replace(tzinfo=None) > until:
                                continue

                        tokens = msg.get('tokens')
                        if tokens:
                            stats['input'] += tokens.get('input', 0)
                            stats['output'] += tokens.get('output', 0)
                            stats['cached'] += tokens.get('cached', 0)
                            stats['thoughts'] += tokens.get('thoughts', 0)
                            stats['total_processed'] += tokens.get('total', 0)
                            stats['total_turns'] += 1
                            
                            model = msg.get('model', 'unknown')
                            stats['models'][model] += tokens.get('total', 0)
                            
                            stats['projects'][project_alias]['total'] += tokens.get('total', 0)
                            stats['projects'][project_alias]['input'] += tokens.get('input', 0)
                            stats['projects'][project_alias]['output'] += tokens.get('output', 0)
                            
                            file_tokens += tokens.get('total', 0)
                            file_has_turns = True
                            
                            session_id = data.get('sessionId') if isinstance(data, dict) else msg.get('sessionId', 'unknown_session')
                            session_tracker[session_id]['tokens'] += tokens.get('total', 0)
                            session_tracker[session_id]['project_alias'] = project_alias
                            if msg_time and session_tracker[session_id]['last_updated'] < msg_time:
                                session_tracker[session_id]['last_updated'] = msg_time

        except Exception as e:
            import traceback
            print(f"Error processing {file_path}: {e}")
            traceback.print_exc()

        if file_has_turns:
            stats['total_sessions'] += 1

    # Convert default dicts back to standard dicts for clean return
    stats['models'] = dict(stats['models'])
    stats['projects'] = dict(stats['projects'])

    return stats
