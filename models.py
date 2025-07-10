"""
Data models for the European Youth Portal Scraper.
Uses Pydantic for data validation and type safety.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
import re
from enum import Enum


class OpportunityStatus(str, Enum):
    """Enumeration for opportunity status."""
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"
    PENDING = "pending"


class FundingProgramme(str, Enum):
    """Enumeration for funding programmes."""
    ERASMUS_PLUS = "erasmus_plus"
    ESC = "european_solidarity_corps"
    YOUTH_PROGRAMME = "youth_programme"
    OTHER = "other"


class OpportunityBase(BaseModel):
    """Base model for opportunity data."""
    opid: str = Field(..., description="Unique opportunity identifier")
    title: str = Field(..., min_length=1, description="Opportunity title")
    url: str = Field(..., description="Opportunity detail URL")
    
    @validator('opid', pre=True)
    def convert_opid_to_string(cls, v):
        """Convert opid to string if it's an integer."""
        return str(v)
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True


class OpportunityDetail(OpportunityBase):
    """Detailed opportunity model with all scraped information."""
    description: Optional[str] = Field(None, description="Detailed description")
    accommodation_food_transport: Optional[str] = Field(None, description="Accommodation and logistics info")
    participant_profile: Optional[str] = Field(None, description="Required participant profile")
    activity_dates: Optional[str] = Field(None, description="Activity date information")
    activity_location: Optional[str] = Field(None, description="Location of the activity")
    looking_for_participants_from: Optional[str] = Field(None, description="Target countries for participants")
    activity_topics: Optional[str] = Field(None, description="Topics covered in the activity")
    application_deadline: Optional[str] = Field(None, description="Application deadline")
    
    # Additional processed fields
    participant_countries: List[str] = Field(default_factory=list, description="Parsed list of participant countries")
    topics_list: List[str] = Field(default_factory=list, description="Parsed list of topics")
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now, description="When this data was scraped")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @validator('participant_countries', pre=True, always=True)
    def parse_participant_countries(cls, v, values):
        """Parse participant countries from the looking_for_participants_from field."""
        if 'looking_for_participants_from' in values and values['looking_for_participants_from']:
            countries = [country.strip() for country in values['looking_for_participants_from'].split(',')]
            return [country for country in countries if country]
        return []
    
    @validator('topics_list', pre=True, always=True)
    def parse_topics(cls, v, values):
        """Parse topics from the activity_topics field."""
        if 'activity_topics' in values and values['activity_topics']:
            topics = [topic.strip() for topic in values['activity_topics'].split(',')]
            return [topic for topic in topics if topic]
        return []


class QueryFilter(BaseModel):
    """Model for filtering opportunities."""
    countries: Optional[List[str]] = Field(None, description="Filter by participant countries")
    topics: Optional[List[str]] = Field(None, description="Filter by activity topics")
    location_keywords: Optional[List[str]] = Field(None, description="Filter by location keywords")
    title_keywords: Optional[List[str]] = Field(None, description="Filter by title keywords")
    description_keywords: Optional[List[str]] = Field(None, description="Filter by description keywords")
    date_from: Optional[date] = Field(None, description="Filter opportunities from this date")
    date_to: Optional[date] = Field(None, description="Filter opportunities to this date")
    
    class Config:
        str_strip_whitespace = True


class QueryResult(BaseModel):
    """Model for query results."""
    opportunities: List[OpportunityDetail]
    total_count: int
    filtered_count: int
    query_time: float
    filters_applied: QueryFilter
    
    class Config:
        arbitrary_types_allowed = True


class Statistics(BaseModel):
    """Model for statistical data."""
    total_opportunities: int
    countries_stats: Dict[str, int]
    topics_stats: Dict[str, int]
    locations_stats: Dict[str, int]
    recent_additions: int
    last_update: datetime
    
    class Config:
        arbitrary_types_allowed = True


class ScrapingSession(BaseModel):
    """Model for tracking scraping sessions."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_opportunities_found: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    errors: List[str] = Field(default_factory=list)
    status: str = "running"  # running, completed, failed
    
    class Config:
        arbitrary_types_allowed = True 