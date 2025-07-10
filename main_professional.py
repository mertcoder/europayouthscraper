"""
European Youth Portal Scraper - Professional Edition
====================================================

A comprehensive, professional-grade web scraper and data analysis tool
for European Youth Portal opportunities with advanced features:

- Async web scraping with rate limiting
- SQLite database with ORM support
- Advanced querying and filtering
- Data analytics and visualization
- Professional CLI interface
- Export capabilities (CSV, Excel, JSON)
- Interactive data exploration

Usage:
    python main_professional.py --help
    python main_professional.py scrape
    python main_professional.py query --country Turkey --topic "Environment"
    python main_professional.py stats
    python main_professional.py export --format excel
    python main_professional.py interactive

Author: European Youth Portal Scraper Team
Version: 2.0.0
License: MIT
"""

import asyncio
import sys
import logging
from pathlib import Path

# Ensure all our modules can be imported
try:
    from cli import cli
    from database import DatabaseManager
    from scraper import ProfessionalScraper
    from analytics import OpportunityAnalytics
    from models import *
    from config import logging_config, scraping_config, database_config
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """Setup comprehensive logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, logging_config.log_level),
        format=logging_config.log_format,
        handlers=[
            logging.FileHandler(log_dir / logging_config.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("European Youth Portal Scraper - Professional Edition v2.0.0 started")
    return logger


def check_dependencies():
    """Check if all required dependencies are available."""
    # Mapping of package names to import names
    required_modules = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'pydantic': 'pydantic',
        'sqlalchemy': 'sqlalchemy',
        'pandas': 'pandas',
        'click': 'click',
        'rich': 'rich',
        'aiohttp': 'aiohttp',
        'plotly': 'plotly',
        'tqdm': 'tqdm',
        'asyncio-throttle': 'asyncio_throttle',
        'python-dateutil': 'dateutil',
        'tabulate': 'tabulate',
        'openpyxl': 'openpyxl',
        'lxml': 'lxml'
    }
    
    missing_modules = []
    for package_name, import_name in required_modules.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_modules.append(package_name)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True


def initialize_database():
    """Initialize database and return database manager."""
    try:
        db_manager = DatabaseManager()
        logger.info("Database initialized successfully")
        return db_manager
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"❌ Database Error: {e}")
        sys.exit(1)


def run_analytics_demo():
    """Demonstrate analytics capabilities."""
    print("🎯 Running Analytics Demo...")
    
    db_manager = initialize_database()
    analytics = OpportunityAnalytics(db_manager)
    
    if analytics.df is None or analytics.df.empty:
        print("⚠️  No data available for analytics. Please run scraping first.")
        return
    
    # Generate insights
    insights = analytics.generate_insights_report()
    
    print(f"\n📊 Analytics Overview:")
    print(f"   • Total Opportunities: {insights['overview']['total_opportunities']}")
    print(f"   • Unique Countries: {insights['overview']['unique_countries']}")
    print(f"   • Unique Topics: {insights['overview']['unique_topics']}")
    print(f"   • Avg Countries/Opportunity: {insights['overview']['avg_countries_per_opportunity']:.1f}")
    print(f"   • Avg Topics/Opportunity: {insights['overview']['avg_topics_per_opportunity']:.1f}")
    
    # Show top countries
    if insights['country_analysis']['country_frequency']:
        print(f"\n🌍 Top 5 Countries:")
        for i, (country, count) in enumerate(list(insights['country_analysis']['country_frequency'].items())[:5], 1):
            print(f"   {i}. {country}: {count} opportunities")
    
    # Show top topics
    if insights['topic_analysis']['topic_frequency']:
        print(f"\n🎯 Top 5 Topics:")
        for i, (topic, count) in enumerate(list(insights['topic_analysis']['topic_frequency'].items())[:5], 1):
            print(f"   {i}. {topic}: {count} opportunities")
    
    # Show recommendations
    if insights['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(insights['recommendations'][:3], 1):
            print(f"   {i}. {rec}")


def run_quick_demo():
    """Run a quick demonstration of key features."""
    print("🚀 European Youth Portal Scraper - Quick Demo")
    print("=" * 50)
    
    db_manager = initialize_database()
    
    # Check if we have data
    stats = db_manager.get_statistics()
    
    if stats.total_opportunities == 0:
        print("⚠️  No data found in database.")
        print("Run 'python main_professional.py scrape' to collect data first.")
        return
    
    print(f"📊 Database contains {stats.total_opportunities} opportunities")
    
    # Show some quick stats
    print(f"\n🌍 Top 5 Countries:")
    for i, (country, count) in enumerate(list(stats.countries_stats.items())[:5], 1):
        print(f"   {i}. {country}: {count} opportunities")
    
    print(f"\n🎯 Top 5 Topics:")
    for i, (topic, count) in enumerate(list(stats.topics_stats.items())[:5], 1):
        print(f"   {i}. {topic}: {count} opportunities")
    
    print(f"\n📈 Recent Activity:")
    print(f"   • Recent additions (7 days): {stats.recent_additions}")
    print(f"   • Last update: {stats.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🔧 Available Commands:")
    print(f"   • Scrape new data: python main_professional.py scrape")
    print(f"   • Query data: python main_professional.py query --country Turkey")
    print(f"   • View stats: python main_professional.py stats")
    print(f"   • Export data: python main_professional.py export --format excel")
    print(f"   • Interactive mode: python main_professional.py interactive")


def main():
    """Main entry point for the professional scraper."""
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup logging
    global logger
    logger = setup_logging()
    
    # If no arguments provided, show demo
    if len(sys.argv) == 1:
        run_quick_demo()
        print(f"\n💡 Use --help to see all available commands")
        return
    
    # If analytics demo requested
    if len(sys.argv) == 2 and sys.argv[1] == "analytics-demo":
        run_analytics_demo()
        return
    
    # Run CLI
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 