# 🇪🇺 European Youth Portal Scraper - Professional Edition

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)](#)
[![CI Status](https://img.shields.io/badge/CI-passing-brightgreen.svg)](#)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](#)

A comprehensive, professional-grade web scraper and data analysis tool for collecting and analyzing youth opportunities from the European Youth Portal. Features advanced async scraping, database management, powerful querying, analytics, and visualization capabilities.

## ✨ Features

### 🔥 Core Features
- **Async Web Scraping**: High-performance concurrent scraping with rate limiting
- **Database Integration**: SQLite database with ORM support and advanced querying
- **Professional CLI**: Beautiful command-line interface with rich formatting
- **Data Analytics**: Comprehensive analytics with insights and visualizations
- **Multiple Export Formats**: CSV, Excel, JSON export capabilities
- **Interactive Mode**: Guided data exploration interface

### 🛠️ Technical Features
- **Type Safety**: Full Pydantic model validation and type hints
- **Error Handling**: Robust error handling with retry mechanisms
- **Logging**: Comprehensive logging with file and console output
- **Configuration**: Centralized configuration management
- **Performance**: Optimized for large-scale data collection
- **Monitoring**: Session tracking and performance metrics

### 📊 Analytics & Insights
- Country-based analysis and statistics
- Topic frequency and co-occurrence analysis
- Temporal trends and growth analysis
- Content quality metrics
- Interactive visualizations with Plotly
- Automated recommendations

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/mertcoder/europayouthscraper
cd europayouthscraper
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run a quick demo:**
```bash
python main_professional.py
```

## 📸 Screenshots & Examples

### CLI Interface

#### Main Help Screen

![image](https://github.com/user-attachments/assets/efc3622a-0068-4948-8015-54cab01da0ed)

#### Stats Screen

![image](https://github.com/user-attachments/assets/932bf5fe-418d-4f12-8484-67b7179be854)

#### Export Queried Country as Excel Screen

![image](https://github.com/user-attachments/assets/bb5b09ca-019b-4842-8787-3a02ef2cc8e7)



### 🐳 Docker Installation

Alternatively, use Docker for a containerized environment:

1. **Build and run with Docker:**
```bash
# Build the image
docker build -t european-youth-scraper .

# Run interactively
docker run -it --rm -v $(pwd)/logs:/app/logs european-youth-scraper

# Run specific commands
docker run --rm european-youth-scraper python main_professional.py stats
```

2. **Use Docker Compose:**
```bash
# Run basic scraper
docker-compose up scraper

# Development environment
docker-compose --profile development up dev

# Full production stack with PostgreSQL
docker-compose --profile production up
```

### Basic Usage

```bash
# Scrape fresh data
python main_professional.py scrape

# Query opportunities by country
python main_professional.py query --country "Turkey" --limit 10

# View comprehensive statistics
python main_professional.py stats

# Export data to Excel
python main_professional.py export --format excel

# Launch interactive mode
python main_professional.py interactive

# Show help
python main_professional.py --help
```

## 📋 Command Reference

### Core Commands

#### `scrape` - Data Collection
```bash
python main_professional.py scrape [OPTIONS]

Options:
  --workers INTEGER       Number of concurrent workers (default: 10)
  --rate-limit FLOAT     Rate limit delay in seconds (default: 5.0)
  --backup/--no-backup   Auto backup to JSON (default: true)
```

#### `query` - Advanced Querying
```bash
python main_professional.py query [OPTIONS]

Options:
  --country TEXT         Filter by participant countries (multiple allowed)
  --topic TEXT          Filter by activity topics (multiple allowed)
  --location TEXT       Filter by location keywords (multiple allowed)
  --title TEXT          Filter by title keywords (multiple allowed)
  --description TEXT    Filter by description keywords (multiple allowed)
  --limit INTEGER       Maximum results to show (default: 20)
  --format [table|json|detailed]  Output format (default: table)
  --export TEXT         Export results to file
```

#### `stats` - Statistics & Analytics
```bash
python main_professional.py stats [OPTIONS]

Options:
  --format [table|json]  Output format (default: table)
```

#### `export` - Data Export
```bash
python main_professional.py export [OPTIONS]

Options:
  --format [csv|excel|json]  Export format (required)
  --filename TEXT           Output filename (auto-generated if not provided)
  --country TEXT           Filter by countries before export
  --topic TEXT             Filter by topics before export
```

#### `details` - Opportunity Details
```bash
python main_professional.py details OPID

Arguments:
  OPID  Opportunity ID to display
```

#### `interactive` - Interactive Mode
```bash
python main_professional.py interactive
```

## 📊 Analytics Features

### Country Analysis
- Participant country frequency analysis
- Location distribution mapping
- Country co-occurrence patterns
- Geographic insights

### Topic Analysis
- Topic popularity trends
- Topic co-occurrence networks
- Thematic clustering
- Content categorization

### Temporal Analysis
- Opportunity discovery timeline
- Growth trend analysis
- Seasonal patterns
- Recent activity tracking

### Content Analysis
- Description quality metrics
- Data completeness assessment
- Common keywords extraction
- Content length statistics

## 🗄️ Database Schema

The application uses SQLite with the following main tables:

### Opportunities Table
```sql
CREATE TABLE opportunities (
    opid TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    accommodation_food_transport TEXT,
    participant_profile TEXT,
    activity_dates TEXT,
    activity_location TEXT,
    looking_for_participants_from TEXT,
    activity_topics TEXT,
    application_deadline TEXT,
    participant_countries JSON,
    topics_list JSON,
    scraped_at DATETIME,
    last_updated DATETIME
);
```

### Scraping Sessions Table
```sql
CREATE TABLE scraping_sessions (
    session_id TEXT PRIMARY KEY,
    start_time DATETIME,
    end_time DATETIME,
    total_opportunities_found INTEGER,
    successful_scrapes INTEGER,
    failed_scrapes INTEGER,
    errors JSON,
    status TEXT
);
```

## 🔧 Configuration

Configuration is managed through `config.py`:

### Scraping Configuration
```python
@dataclass
class ScrapingConfig:
    max_workers: int = 10
    page_size: int = 100
    request_timeout: int = 20
    rate_limit_delay: float = 5.0
    max_retries: int = 3
```

### Database Configuration
```python
@dataclass
class DatabaseConfig:
    db_path: str = "opportunities.db"
    json_backup_path: str = "structured_opportunities.json"
    auto_backup: bool = True
```

### Logging Configuration
```python
@dataclass
class LoggingConfig:
    log_level: str = "INFO"
    log_file: str = "scraper.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
```

## 📈 Performance & Monitoring

### Performance Features
- **Async Operations**: Non-blocking I/O for maximum throughput
- **Connection Pooling**: Efficient HTTP connection management
- **Rate Limiting**: Respectful scraping with configurable delays
- **Retry Logic**: Exponential backoff for failed requests
- **Progress Tracking**: Real-time progress monitoring

### Monitoring
- **Session Tracking**: Detailed scraping session metadata
- **Error Logging**: Comprehensive error tracking and reporting
- **Performance Metrics**: Request timing and success rates
- **Health Checks**: Database and connection health monitoring

## 🎯 Example Workflows

### 1. Complete Data Collection Pipeline
```bash
# 1. Scrape fresh data with custom settings
python main_professional.py scrape --workers 15 --rate-limit 3.0

# 2. Analyze the data
python main_professional.py stats

# 3. Query specific opportunities
python main_professional.py query --country "Germany" --topic "Environment"

# 4. Export filtered results
python main_professional.py export --format excel --country "Turkey"
```

### 2. Analytics Workflow
```bash
# Generate comprehensive analytics
python main_professional.py analytics-demo

# View detailed statistics
python main_professional.py stats --format json > analytics_report.json

# Export for external analysis
python main_professional.py export --format csv --filename "full_dataset.csv"
```

### 3. Interactive Exploration
```bash
# Launch interactive mode for guided exploration
python main_professional.py interactive

# Or use specific queries
python main_professional.py query --topic "Youth" --location "Italy" --format detailed
```

## 🔍 Advanced Querying Examples

### Multi-filter Queries
```bash
# Complex filtering
python main_professional.py query \
  --country "Turkey" \
  --country "Germany" \
  --topic "Environment" \
  --topic "Culture" \
  --location "Berlin" \
  --limit 50 \
  --format detailed \
  --export "filtered_opportunities.json"
```

### Keyword Searches
```bash
# Search in titles and descriptions
python main_professional.py query \
  --title "volunteer" \
  --title "internship" \
  --description "climate" \
  --description "sustainability"
```

## 🛡️ Error Handling & Reliability

### Retry Mechanisms
- Exponential backoff for failed requests
- Automatic retry on rate limiting (HTTP 429)
- Connection timeout handling
- Graceful degradation on partial failures

### Data Validation
- Pydantic model validation for all data
- Type checking and constraint validation
- Automatic data cleaning and normalization
- Comprehensive error reporting

### Monitoring & Logging
- Detailed logging to file and console
- Session-based error tracking
- Performance metrics collection
- Health check capabilities

## 📊 Sample Analytics Output

```
📊 Analytics Overview:
   • Total Opportunities: 1,245
   • Unique Countries: 28
   • Unique Topics: 45
   • Avg Countries/Opportunity: 3.2
   • Avg Topics/Opportunity: 2.8

🌍 Top 5 Countries:
   1. Germany: 156 opportunities
   2. France: 142 opportunities
   3. Italy: 134 opportunities
   4. Spain: 128 opportunities
   5. Poland: 95 opportunities

🎯 Top 5 Topics:
   1. Environment: 234 opportunities
   2. Culture: 198 opportunities
   3. Education: 187 opportunities
   4. Youth: 156 opportunities
   5. Social: 145 opportunities

💡 Recommendations:
   1. Topic diversity could be improved. Currently 45 unique topics are covered.
   2. Improve data quality for participant_profile: only 78.5% complete
   3. Consider expanding to more Eastern European countries
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page for existing solutions
2. Create a new issue with detailed information
3. Use the `--help` flag for command-specific assistance
4. Check the log files in the `logs/` directory for debugging

## 🏗️ Architecture

```
European Youth Portal Scraper - Professional Edition
├── config.py              # Configuration management
├── models.py               # Pydantic data models
├── database.py             # Database layer (SQLAlchemy)
├── scraper.py              # Async web scraping engine
├── analytics.py            # Data analytics and insights
├── cli.py                  # Professional CLI interface
├── main_professional.py    # Main application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎉 What's New in v2.0.0

- **Complete Rewrite**: Professional-grade architecture
- **Async Support**: 5x faster data collection
- **Advanced Analytics**: Comprehensive insights and visualizations
- **Beautiful CLI**: Rich formatting and interactive modes
- **Type Safety**: Full Pydantic validation
- **Database Integration**: SQLite with ORM support
- **Export Capabilities**: Multiple format support
- **Monitoring**: Session tracking and performance metrics
- **Configuration**: Centralized config management
- **Documentation**: Comprehensive usage guide

---

**Made with ❤️ for the European Youth Community** 
