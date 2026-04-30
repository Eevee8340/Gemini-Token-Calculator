import os
from pathlib import Path

def get_gemini_dir() -> Path:
    """
    Auto-detect the Gemini CLI directory across different operating systems.
    Returns a Path object to the .gemini directory.
    """
    # Use standard Path.home() which resolves to %USERPROFILE% on Windows and ~ on POSIX.
    home = Path.home()
    gemini_dir = home / ".gemini"
    
    if not gemini_dir.exists():
        # Fallback or edge cases if needed
        pass
        
    return gemini_dir

def get_projects_json_path() -> Path:
    """Returns the path to the projects.json mapping file."""
    return get_gemini_dir() / "projects.json"

def get_tmp_dir() -> Path:
    """Returns the path to the temporary workspaces/chats folder."""
    return get_gemini_dir() / "tmp"
