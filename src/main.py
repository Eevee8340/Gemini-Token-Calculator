import argparse
import os
import sys
from datetime import datetime
from rich.console import Console
from .config import get_tmp_dir
from .parser import calculate_tokens
from .display import display_stats

console = Console()

def is_run_from_explorer() -> bool:
    """Returns True if the script was launched directly from Windows Explorer."""
    if os.name != 'nt':
        return False
    try:
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        # GetConsoleProcessList returns the number of processes attached to the console
        # If run from cmd/powershell, there's at least the shell + this process (>=2).
        # If launched directly, it's usually just this process (1) or with a launcher (2).
        process_list = (ctypes.c_uint * 10)()
        num_processes = kernel32.GetConsoleProcessList(process_list, 10)
        return num_processes <= 2
    except Exception:
        return False

def parse_date(date_str: str) -> datetime:
    """Helper to parse CLI date strings."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or ISO 8601.")

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI Token Usage Calculator")
    parser.add_argument("--since", type=parse_date, help="Filter out sessions older than this date (e.g. 2026-04-01)")
    parser.add_argument("--until", type=parse_date, help="Filter out sessions newer than this date (e.g. 2026-04-30)")
    parser.add_argument("--export", choices=['json', 'csv'], help="Export format (bypasses UI output)")
    
    args = parser.parse_args()
    
    tmp_dir = get_tmp_dir()
    
    if not tmp_dir.exists():
        if not args.export:
            console.print(f"[bold red]Error:[/] Gemini CLI tmp directory not found at {tmp_dir}")
        return

    if not args.export:
        # Use rich progress bar if not exporting raw data
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scanning Gemini CLI history and calculating tokens...", total=None)
            stats = calculate_tokens(tmp_dir, since=args.since, until=args.until)
            progress.update(task, completed=True)
            
    else:
        # Run silently if exporting
        stats = calculate_tokens(tmp_dir, since=args.since, until=args.until)

    display_stats(stats, is_export_json=(args.export == 'json'), is_export_csv=(args.export == 'csv'))

    if not args.export and is_run_from_explorer():
        console.print("\n[dim]Press Enter to exit...[/dim]")
        input()

if __name__ == "__main__":
    main()
