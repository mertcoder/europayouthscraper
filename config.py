"""
Configuration settings for the European Youth Portal Scraper.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""
    base_url: str = "https://youth.europa.eu/api/rest/eyp/v1/search_en"
    detail_url_template: str = "https://youth.europa.eu/solidarity/opportunity/{opid}_en"
    max_workers: int = 15
    page_size: int = 100
    request_timeout: int = 20
    rate_limit_delay: float = 1.5
    max_retries: int = 4
    retry_delay: float = 2.0


@dataclass
class DatabaseConfig:
    """Configuration for database operations."""
    db_path: str = "opportunities.db"
    json_backup_path: str = "structured_opportunities.json"
    auto_backup: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    log_level: str = "INFO"
    log_file: str = "scraper.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


# User agent rotation for avoiding bot detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
]

# API request parameters
API_PARAMS = {
    'type': 'Opportunity',
    'filters[status]': 'open',
    'filters[date_end][operator]': '>=',
    'filters[date_end][value]': '2025-07-10',
    'filters[date_end][type]': 'must',
    'filters[funding_programme][id][0]': 5,
    'filters[funding_programme][id][1]': 4,
    'filters[funding_programme][id][2]': 3,
    'filters[funding_programme][id][3]': 2,
    'filters[funding_programme][id][4]': 1,
    'filters[funding_programme][id][5]': 8,
    'filters[funding_programme][id][6]': 6,
    'filters[funding_programme][id][7]': 7,
    'filters[date_application_end][operator]': '>=',
    'filters[date_application_end][value]': '2025-07-10',
    'filters[date_application_end][type]': 'must',
    'filters[date_application_end][group]': 'deadline',
    'filters[has_no_deadline][value]': 'true',
    'filters[has_no_deadline][type]': 'must',
    'filters[has_no_deadline][group]': 'deadline',
    'fields[0]': 'opid',
    'fields[1]': 'title',
    'sort[created]': 'desc'
}

# Data extraction mapping
SECTION_MAPPINGS = {
    "Description": "description",
    "Accommodation, food and transport arrangements": "accommodation_food_transport",
    "Participant profile": "participant_profile",
    "Activity dates": "activity_dates",
    "Activity location": "activity_location",
    "Looking for participants from": "looking_for_participants_from",
    "Activity topics": "activity_topics",
    "Deadline for applications": "application_deadline"
}

# Default configuration instances
scraping_config = ScrapingConfig()
database_config = DatabaseConfig()
logging_config = LoggingConfig() 