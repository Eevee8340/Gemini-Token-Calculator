import json
from pathlib import Path
from .config import get_projects_json_path

def get_project_mapping() -> dict:
    """
    Reads the ~/.gemini/projects.json file and returns a reverse mapping
    so we can look up the original directory path using the hash/alias.
    
    Returns:
        A dictionary like {'fern': 'c:\\users\\gaurav\\fern'}
    """
    mapping = {}
    json_path = get_projects_json_path()
    
    if not json_path.exists():
        return mapping
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            projects = data.get("projects", {})
            # Reverse the mapping: alias/hash -> local path
            for path, alias in projects.items():
                mapping[alias] = path
    except Exception as e:
        # Silently fail or log debug if needed
        pass
        
    return mapping

def get_project_name(alias: str, mapping: dict) -> str:
    """
    Given an alias/hash (like 'fern' or '37a827e0-f40c-4a14-af36-78141ef07e5d'),
    returns the mapped human-readable path if it exists, otherwise returns the alias itself.
    """
    return mapping.get(alias, alias)
