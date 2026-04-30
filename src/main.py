import argparse
from datetime import datetime
from rich.console import Console
from .config import get_tmp_dir
from .parser import calculate_tokens
from .display import display_stats

console = Console()

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

if __name__ == "__main__":
    main()
