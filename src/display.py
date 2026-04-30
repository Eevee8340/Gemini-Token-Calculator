from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import json
import csv
import sys
import os
from pathlib import Path
from .projects import get_project_name, get_project_mapping

console = Console()

def format_number(num: int) -> str:
    """Formats an integer with commas for readability."""
    return f"{num:,}"

def sanitize_path(path: str) -> str:
    """Sanitizes the path to hide the user's home directory name."""
    try:
        home_dir = str(Path.home())
        if path.lower().startswith(home_dir.lower()):
            # Replace home directory with ~
            return "~" + path[len(home_dir):]
        # Alternatively, just return the basename if it's a raw hash or something long
        if len(path) > 40 and '\\' not in path and '/' not in path:
            return path[:8] + "..."
        return path
    except Exception:
        return path

def display_stats(stats: dict, is_export_json: bool = False, is_export_csv: bool = False):
    """
    Renders the parsed statistics into a rich terminal UI,
    or exports them to stdout if requested.
    """
    project_mapping = get_project_mapping()

    if is_export_json:
        # Add human readable project names to the export
        export_stats = dict(stats)
        if 'top_sessions' in export_stats:
            del export_stats['top_sessions']
            
        for alias, data in export_stats.get('projects', {}).items():
            data['human_readable_path'] = sanitize_path(get_project_name(alias, project_mapping))
        print(json.dumps(export_stats, indent=2))
        return

    if is_export_csv:
        # Simple CSV export of project breakdown
        writer = csv.writer(sys.stdout)
        writer.writerow(["Project Path", "Alias", "Total Tokens", "Input Tokens", "Output Tokens"])
        for alias, data in stats.get('projects', {}).items():
            path = sanitize_path(get_project_name(alias, project_mapping))
            writer.writerow([path, alias, data['total'], data['input'], data['output']])
        return

    # Rich Terminal Output

    # 1. Overall Summary Panel
    summary_text = Text()
    summary_text.append(f"Total Sessions: ", style="bold cyan")
    summary_text.append(f"{format_number(stats['total_sessions'])}\n")
    summary_text.append(f"Total Turns:    ", style="bold cyan")
    summary_text.append(f"{format_number(stats['total_turns'])}\n\n")
    
    summary_text.append(f"Total Tokens Processed: ", style="bold green")
    summary_text.append(f"{format_number(stats['total_processed'])}\n")
    
    summary_text.append(f"  ├─ Input Tokens:    ", style="dim")
    summary_text.append(f"{format_number(stats['input'])}\n")
    
    summary_text.append(f"  ├─ Output Tokens:   ", style="dim")
    summary_text.append(f"{format_number(stats['output'])}\n")
    
    summary_text.append(f"  ├─ Cached Tokens:   ", style="dim")
    summary_text.append(f"{format_number(stats['cached'])}\n")
    
    summary_text.append(f"  └─ Thoughts Tokens: ", style="dim")
    summary_text.append(f"{format_number(stats['thoughts'])}")
    
    console.print(Panel(summary_text, title="📊 Gemini CLI Token Usage Summary", expand=False, border_style="cyan"))
    
    # 2. Top 5 Projects Table
    project_table = Table(title="📁 Top 5 Projects by Token Usage", show_header=True, header_style="bold magenta")
    project_table.add_column("Project Path", style="cyan", no_wrap=False)
    project_table.add_column("Total Tokens", justify="right", style="green")
    project_table.add_column("Input", justify="right", style="dim")
    project_table.add_column("Output", justify="right", style="dim")
    
    # Sort projects by total tokens descending and take top 5
    sorted_projects = sorted(stats['projects'].items(), key=lambda item: item[1]['total'], reverse=True)[:5]
    
    for alias, p_stats in sorted_projects:
        human_path = get_project_name(alias, project_mapping)
        sanitized_path = sanitize_path(human_path)
        
        # Handle long paths gracefully
        if len(sanitized_path) > 50:
            sanitized_path = "..." + sanitized_path[-47:]
        
        project_table.add_row(
            sanitized_path,
            format_number(p_stats['total']),
            format_number(p_stats['input']),
            format_number(p_stats['output'])
        )
    
    console.print(project_table)
    
    # 3. Model Breakdown Table
    model_table = Table(title="🤖 Token Usage by Model", show_header=True, header_style="bold yellow")
    model_table.add_column("Model Name", style="cyan")
    model_table.add_column("Total Tokens", justify="right", style="green")
    
    sorted_models = sorted(stats['models'].items(), key=lambda item: item[1], reverse=True)
    for model, tokens in sorted_models:
        model_table.add_row(model, format_number(tokens))
        
    console.print(model_table)

