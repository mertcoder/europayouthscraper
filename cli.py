"""
Professional CLI interface for the European Youth Portal Scraper.
Uses Click for command handling and Rich for beautiful output formatting.
"""

import asyncio
import click
import logging
import json
import sys
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.tree import Tree
from rich.json import JSON
from rich.prompt import Prompt, Confirm
from tabulate import tabulate
import pandas as pd

from database import DatabaseManager
from scraper import ProfessionalScraper
from models import QueryFilter, OpportunityDetail
from config import logging_config

# Initialize Rich console
console = Console()

# Setup logging
logging.basicConfig(
    level=getattr(logging, logging_config.log_level),
    format=logging_config.log_format,
    handlers=[
        logging.FileHandler(logging_config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="2.0.0", prog_name="European Youth Portal Scraper")
@click.option('--db-path', default="opportunities.db", help='Database file path')
@click.pass_context
def cli(ctx, db_path):
    """🇪🇺 European Youth Portal Scraper - Professional Edition
    
    Advanced web scraper for collecting and analyzing youth opportunities
    from the European Youth Portal with powerful querying capabilities.
    """
    ctx.ensure_object(dict)
    ctx.obj['db_manager'] = DatabaseManager(db_path)
    
    # Welcome message
    console.print(Panel.fit(
        "[bold blue]🇪🇺 European Youth Portal Scraper[/bold blue]\n"
        "[dim]Professional Edition v2.0.0[/dim]",
        border_style="blue"
    ))


@cli.command()
@click.option('--workers', default=10, help='Number of concurrent workers')
@click.option('--rate-limit', default=5.0, help='Rate limit delay in seconds')
@click.option('--backup/--no-backup', default=True, help='Auto backup to JSON')
@click.pass_context
def scrape(ctx, workers, rate_limit, backup):
    """🔍 Scrape fresh data from the European Youth Portal
    
    Performs full data collection using async operations with
    configurable concurrency and rate limiting.
    """
    db_manager = ctx.obj['db_manager']
    
    console.print("\n[bold yellow]🚀 Starting Professional Scraping Pipeline[/bold yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        task = progress.add_task("Initializing scraper...", total=None)
        
        # Progress callback function for real-time updates
        def update_progress(completed, total, percentage, successful):
            progress.update(task, 
                          description=f"Scraping: {completed}/{total} ({successful} successful)",
                          completed=completed,
                          total=total)
        
        # Initialize scraper with progress callback
        scraper = ProfessionalScraper(db_manager, progress_callback=update_progress)
        
        # Configure scraper
        scraper.config.max_workers = workers
        scraper.config.rate_limit_delay = rate_limit
        
        # Configure backup (import here to avoid circular imports)
        from config import database_config
        database_config.auto_backup = backup
        
        progress.update(task, description="Getting opportunities list...")
        
        # Run async pipeline
        try:
            saved_count = asyncio.run(scraper.run_full_scraping_pipeline())
            
            progress.update(task, description="✅ Scraping completed!", completed=True)
            
            # Show results
            stats = scraper.get_session_statistics()
            
            console.print(f"\n[bold green]✅ Scraping Pipeline Completed![/bold green]")
            console.print(f"📊 [bold]Results Summary:[/bold]")
            console.print(f"   • Opportunities Found: [bold cyan]{stats['total_found']}[/bold cyan]")
            console.print(f"   • Successfully Scraped: [bold green]{stats['successful_scrapes']}[/bold green]")
            console.print(f"   • Failed Scrapes: [bold red]{stats['failed_scrapes']}[/bold red]")
            console.print(f"   • Success Rate: [bold blue]{stats['success_rate']:.1f}%[/bold blue]")
            console.print(f"   • Duration: [bold magenta]{stats['duration_seconds']:.2f}s[/bold magenta]")
            console.print(f"   • Saved to Database: [bold yellow]{saved_count}[/bold yellow]")
            
            if stats['errors_count'] > 0:
                console.print(f"\n[bold red]⚠️  {stats['errors_count']} errors occurred during scraping[/bold red]")
                if click.confirm("Show error details?"):
                    for error in stats['errors'][-5:]:  # Show last 5 errors
                        console.print(f"   • [red]{error}[/red]")
        
        except Exception as e:
            progress.update(task, description="❌ Scraping failed!", completed=True)
            console.print(f"[bold red]❌ Scraping failed: {e}[/bold red]")
            sys.exit(1)


@cli.command()
@click.option('--country', multiple=True, help='Filter by participant countries')
@click.option('--topic', multiple=True, help='Filter by activity topics')
@click.option('--location', multiple=True, help='Filter by location keywords')
@click.option('--title', multiple=True, help='Filter by title keywords')
@click.option('--description', multiple=True, help='Filter by description keywords')
@click.option('--limit', default=20, help='Maximum number of results to show')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'detailed']), 
              default='table', help='Output format')
@click.option('--export', help='Export results to file (CSV, Excel, JSON)')
@click.pass_context
def query(ctx, country, topic, location, title, description, limit, output_format, export):
    """🔎 Advanced querying with multiple filters
    
    Search opportunities using sophisticated filtering options.
    Supports multiple output formats and data export.
    """
    db_manager = ctx.obj['db_manager']
    
    # Build query filter
    filters = QueryFilter(
        countries=list(country) if country else None,
        topics=list(topic) if topic else None,
        location_keywords=list(location) if location else None,
        title_keywords=list(title) if title else None,
        description_keywords=list(description) if description else None
    )
    
    console.print("\n[bold blue]🔍 Executing Advanced Query[/bold blue]")
    
    with console.status("[bold green]Searching database..."):
        result = db_manager.query_opportunities(filters)
    
    if not result.opportunities:
        console.print("[yellow]🤷 No opportunities found matching your criteria[/yellow]")
        return
    
    # Apply limit
    limited_opportunities = result.opportunities[:limit]
    
    # Display results
    console.print(f"\n[bold green]📋 Query Results[/bold green]")
    console.print(f"Found {result.filtered_count} opportunities (showing {len(limited_opportunities)})")
    console.print(f"Query time: {result.query_time:.3f} seconds")
    
    if output_format == 'table':
        _display_table_format(limited_opportunities)
    elif output_format == 'json':
        _display_json_format(limited_opportunities)
    elif output_format == 'detailed':
        _display_detailed_format(limited_opportunities)
    
    # Export if requested
    if export:
        _export_results(result.opportunities, export, console)


@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), 
              default='table', help='Output format')
@click.pass_context
def stats(ctx, output_format):
    """📊 Show comprehensive database statistics
    
    Display detailed statistics about opportunities, countries, topics, and trends.
    """
    db_manager = ctx.obj['db_manager']
    
    console.print("\n[bold blue]📊 Database Statistics[/bold blue]")
    
    with console.status("[bold green]Generating statistics..."):
        statistics = db_manager.get_statistics()
    
    if output_format == 'json':
        console.print(JSON(statistics.json()))
        return
    
    # Table format
    console.print(f"\n[bold green]📈 Overview[/bold green]")
    console.print(f"Total Opportunities: [bold cyan]{statistics.total_opportunities}[/bold cyan]")
    console.print(f"Recent Additions (7 days): [bold yellow]{statistics.recent_additions}[/bold yellow]")
    console.print(f"Last Update: [bold magenta]{statistics.last_update.strftime('%Y-%m-%d %H:%M:%S')}[/bold magenta]")
    
    # Top countries
    if statistics.countries_stats:
        console.print(f"\n[bold green]🌍 Top Countries (Participant Opportunities)[/bold green]")
        countries_table = Table(show_header=True, header_style="bold blue")
        countries_table.add_column("Country", style="dim")
        countries_table.add_column("Opportunities", justify="right", style="bold cyan")
        
        for country, count in list(statistics.countries_stats.items())[:10]:
            countries_table.add_row(country, str(count))
        
        console.print(countries_table)
    
    # Top topics
    if statistics.topics_stats:
        console.print(f"\n[bold green]🎯 Top Topics[/bold green]")
        topics_table = Table(show_header=True, header_style="bold blue")
        topics_table.add_column("Topic", style="dim")
        topics_table.add_column("Opportunities", justify="right", style="bold cyan")
        
        for topic, count in list(statistics.topics_stats.items())[:10]:
            topics_table.add_row(topic, str(count))
        
        console.print(topics_table)


@cli.command()
@click.argument('opid')
@click.pass_context
def details(ctx, opid):
    """📄 Show detailed information for a specific opportunity
    
    Display comprehensive details for an opportunity by its ID.
    """
    db_manager = ctx.obj['db_manager']
    
    opportunity = db_manager.get_opportunity_by_id(opid)
    
    if not opportunity:
        console.print(f"[red]❌ Opportunity with ID '{opid}' not found[/red]")
        return
    
    # Create detailed panel
    content = f"""[bold blue]Title:[/bold blue] {opportunity.title}
[bold blue]URL:[/bold blue] {opportunity.url}
[bold blue]Location:[/bold blue] {opportunity.activity_location or 'N/A'}
[bold blue]Countries:[/bold blue] {opportunity.looking_for_participants_from or 'N/A'}
[bold blue]Topics:[/bold blue] {opportunity.activity_topics or 'N/A'}
[bold blue]Dates:[/bold blue] {opportunity.activity_dates or 'N/A'}
[bold blue]Deadline:[/bold blue] {opportunity.application_deadline or 'N/A'}

[bold blue]Description:[/bold blue]
{opportunity.description or 'N/A'}

[bold blue]Participant Profile:[/bold blue]
{opportunity.participant_profile or 'N/A'}

[bold blue]Accommodation & Transport:[/bold blue]
{opportunity.accommodation_food_transport or 'N/A'}"""
    
    console.print(Panel(content, title=f"Opportunity Details - {opid}", border_style="blue"))


@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['csv', 'excel', 'json']), 
              required=True, help='Export format')
@click.option('--filename', help='Output filename (auto-generated if not provided)')
@click.option('--country', multiple=True, help='Filter by countries before export')
@click.option('--topic', multiple=True, help='Filter by topics before export')
@click.pass_context
def export(ctx, output_format, filename, country, topic):
    """💾 Export data to various formats
    
    Export opportunities data to CSV, Excel, or JSON formats with optional filtering.
    """
    db_manager = ctx.obj['db_manager']
    
    # Build filters if provided
    filters = None
    if country or topic:
        filters = QueryFilter(
            countries=list(country) if country else None,
            topics=list(topic) if topic else None
        )
    
    console.print(f"\n[bold blue]💾 Exporting Data[/bold blue]")
    
    with console.status("[bold green]Preparing export..."):
        df = db_manager.export_to_pandas(filters)
    
    if df.empty:
        console.print("[yellow]No data to export[/yellow]")
        return
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == 'excel':
            filename = f"opportunities_export_{timestamp}.xlsx"
        else:
            filename = f"opportunities_export_{timestamp}.{output_format}"
    
    try:
        if output_format == 'csv':
            df.to_csv(filename, index=False, encoding='utf-8')
        elif output_format == 'excel':
            df.to_excel(filename, index=False, engine='openpyxl')
        elif output_format == 'json':
            df.to_json(filename, orient='records', force_ascii=False, indent=2)
        
        console.print(f"[bold green]✅ Exported {len(df)} opportunities to {filename}[/bold green]")
    
    except Exception as e:
        console.print(f"[bold red]❌ Export failed: {e}[/bold red]")


@cli.command()
@click.pass_context
def interactive(ctx):
    """🎮 Interactive mode with guided queries
    
    Launch an interactive session for easier data exploration.
    """
    db_manager = ctx.obj['db_manager']
    
    console.print(Panel.fit(
        "[bold green]🎮 Interactive Mode[/bold green]\n"
        "[dim]Follow the prompts to explore opportunities[/dim]",
        border_style="green"
    ))
    
    while True:
        console.print("\n[bold blue]What would you like to do?[/bold blue]")
        console.print("1. Search by country")
        console.print("2. Search by topic")
        console.print("3. Search by keywords")
        console.print("4. Show statistics")
        console.print("5. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            country = Prompt.ask("Enter country name")
            _interactive_search(db_manager, countries=[country])
        
        elif choice == "2":
            topic = Prompt.ask("Enter topic")
            _interactive_search(db_manager, topics=[topic])
        
        elif choice == "3":
            keywords = Prompt.ask("Enter keywords (comma-separated)").split(',')
            keywords = [k.strip() for k in keywords]
            _interactive_search(db_manager, title_keywords=keywords)
        
        elif choice == "4":
            ctx.invoke(stats)
        
        elif choice == "5":
            console.print("[bold green]👋 Goodbye![/bold green]")
            break


def _interactive_search(db_manager, **kwargs):
    """Helper function for interactive searches."""
    filters = QueryFilter(**kwargs)
    result = db_manager.query_opportunities(filters)
    
    if not result.opportunities:
        console.print("[yellow]No opportunities found[/yellow]")
        return
    
    console.print(f"\nFound {result.filtered_count} opportunities:")
    _display_table_format(result.opportunities[:10])
    
    if len(result.opportunities) > 10:
        if Confirm.ask("Show more results?"):
            _display_table_format(result.opportunities[10:20])


def _display_table_format(opportunities: List[OpportunityDetail]):
    """Display opportunities in table format."""
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Title", style="bold", width=40)
    table.add_column("Location", style="cyan", width=20)
    table.add_column("Countries", style="green", width=20)
    
    for opp in opportunities:
        table.add_row(
            opp.opid,
            opp.title[:37] + "..." if len(opp.title) > 40 else opp.title,
            (opp.activity_location or "N/A")[:17] + "..." if (opp.activity_location or "") and len(opp.activity_location) > 20 else (opp.activity_location or "N/A"),
            (opp.looking_for_participants_from or "N/A")[:17] + "..." if (opp.looking_for_participants_from or "") and len(opp.looking_for_participants_from) > 20 else (opp.looking_for_participants_from or "N/A")
        )
    
    console.print(table)


def _display_json_format(opportunities: List[OpportunityDetail]):
    """Display opportunities in JSON format."""
    data = [opp.dict() for opp in opportunities]
    console.print(JSON(json.dumps(data, default=str)))


def _display_detailed_format(opportunities: List[OpportunityDetail]):
    """Display opportunities in detailed format."""
    for i, opp in enumerate(opportunities, 1):
        console.print(f"\n[bold blue]--- Opportunity {i} ---[/bold blue]")
        console.print(f"[bold]ID:[/bold] {opp.opid}")
        console.print(f"[bold]Title:[/bold] {opp.title}")
        console.print(f"[bold]Location:[/bold] {opp.activity_location or 'N/A'}")
        console.print(f"[bold]Countries:[/bold] {opp.looking_for_participants_from or 'N/A'}")
        console.print(f"[bold]URL:[/bold] {opp.url}")


def _export_results(opportunities: List[OpportunityDetail], filename: str, console):
    """Export results to file."""
    try:
        extension = Path(filename).suffix.lower()
        
        if extension == '.json':
            data = [opp.dict() for opp in opportunities]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        elif extension in ['.csv', '.xlsx']:
            df = pd.DataFrame([opp.dict() for opp in opportunities])
            if extension == '.csv':
                df.to_csv(filename, index=False, encoding='utf-8')
            else:
                df.to_excel(filename, index=False, engine='openpyxl')
        
        console.print(f"[bold green]✅ Exported {len(opportunities)} opportunities to {filename}[/bold green]")
    
    except Exception as e:
        console.print(f"[bold red]❌ Export failed: {e}[/bold red]")


if __name__ == '__main__':
    cli() 