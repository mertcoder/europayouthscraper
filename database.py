"""
Database layer for the European Youth Portal Scraper.
Uses SQLAlchemy for ORM and advanced querying capabilities.
"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, JSON, func, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
import pandas as pd

from models import OpportunityDetail, QueryFilter, QueryResult, Statistics, ScrapingSession
from config import database_config

logger = logging.getLogger(__name__)
Base = declarative_base()


class OpportunityDB(Base):
    """SQLAlchemy model for opportunities table."""
    __tablename__ = 'opportunities'
    
    opid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    accommodation_food_transport = Column(Text)
    participant_profile = Column(Text)
    activity_dates = Column(Text)
    activity_location = Column(Text)
    looking_for_participants_from = Column(Text)
    activity_topics = Column(Text)
    application_deadline = Column(Text)
    participant_countries = Column(SQLiteJSON)
    topics_list = Column(SQLiteJSON)
    scraped_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ScrapingSessionDB(Base):
    """SQLAlchemy model for scraping sessions table."""
    __tablename__ = 'scraping_sessions'
    
    session_id = Column(String, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    total_opportunities_found = Column(Integer, default=0)
    successful_scrapes = Column(Integer, default=0)
    failed_scrapes = Column(Integer, default=0)
    errors = Column(SQLiteJSON)
    status = Column(String, default="running")


class DatabaseManager:
    """Professional database manager with advanced querying capabilities."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager."""
        self.db_path = db_path or database_config.db_path
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
        logger.info(f"Database initialized at {self.db_path}")
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def insert_opportunity(self, opportunity: OpportunityDetail) -> bool:
        """Insert or update a single opportunity."""
        try:
            with self.get_session() as session:
                # Check if opportunity exists
                existing = session.query(OpportunityDB).filter_by(opid=opportunity.opid).first()
                
                if existing:
                    # Update existing opportunity
                    for key, value in opportunity.dict().items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.last_updated = datetime.now()
                    logger.debug(f"Updated opportunity {opportunity.opid}")
                else:
                    # Insert new opportunity
                    db_opportunity = OpportunityDB(**opportunity.dict())
                    session.add(db_opportunity)
                    logger.debug(f"Inserted opportunity {opportunity.opid}")
                
                return True
        except Exception as e:
            logger.error(f"Error inserting opportunity {opportunity.opid}: {e}")
            return False
    
    def bulk_insert_opportunities(self, opportunities: List[OpportunityDetail]) -> int:
        """Bulk insert opportunities for better performance."""
        success_count = 0
        try:
            with self.get_session() as session:
                for opportunity in opportunities:
                    try:
                        existing = session.query(OpportunityDB).filter_by(opid=opportunity.opid).first()
                        
                        if existing:
                            for key, value in opportunity.dict().items():
                                if hasattr(existing, key):
                                    setattr(existing, key, value)
                            existing.last_updated = datetime.now()
                        else:
                            db_opportunity = OpportunityDB(**opportunity.dict())
                            session.add(db_opportunity)
                        
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Error with opportunity {opportunity.opid}: {e}")
                        continue
                
                logger.info(f"Bulk inserted/updated {success_count} opportunities")
                return success_count
        except Exception as e:
            logger.error(f"Bulk insert error: {e}")
            return success_count
    
    def query_opportunities(self, filters: QueryFilter) -> QueryResult:
        """Advanced querying with multiple filters."""
        start_time = datetime.now()
        
        try:
            with self.get_session() as session:
                query = session.query(OpportunityDB)
                total_count = query.count()
                
                # Apply filters
                if filters.countries:
                    country_conditions = []
                    for country in filters.countries:
                        country_conditions.append(
                            OpportunityDB.looking_for_participants_from.ilike(f'%{country}%')
                        )
                    query = query.filter(or_(*country_conditions))
                
                if filters.topics:
                    topic_conditions = []
                    for topic in filters.topics:
                        topic_conditions.append(
                            OpportunityDB.activity_topics.ilike(f'%{topic}%')
                        )
                    query = query.filter(or_(*topic_conditions))
                
                if filters.location_keywords:
                    location_conditions = []
                    for keyword in filters.location_keywords:
                        location_conditions.append(
                            OpportunityDB.activity_location.ilike(f'%{keyword}%')
                        )
                    query = query.filter(or_(*location_conditions))
                
                if filters.title_keywords:
                    title_conditions = []
                    for keyword in filters.title_keywords:
                        title_conditions.append(
                            OpportunityDB.title.ilike(f'%{keyword}%')
                        )
                    query = query.filter(or_(*title_conditions))
                
                if filters.description_keywords:
                    desc_conditions = []
                    for keyword in filters.description_keywords:
                        desc_conditions.append(
                            OpportunityDB.description.ilike(f'%{keyword}%')
                        )
                    query = query.filter(or_(*desc_conditions))
                
                # Execute query
                results = query.all()
                
                # Convert to Pydantic models
                opportunities = []
                for result in results:
                    opportunity_dict = {
                        column.name: getattr(result, column.name) 
                        for column in result.__table__.columns
                    }
                    opportunities.append(OpportunityDetail(**opportunity_dict))
                
                query_time = (datetime.now() - start_time).total_seconds()
                
                return QueryResult(
                    opportunities=opportunities,
                    total_count=total_count,
                    filtered_count=len(opportunities),
                    query_time=query_time,
                    filters_applied=filters
                )
        
        except Exception as e:
            logger.error(f"Query error: {e}")
            return QueryResult(
                opportunities=[],
                total_count=0,
                filtered_count=0,
                query_time=0,
                filters_applied=filters
            )
    
    def get_statistics(self) -> Statistics:
        """Generate comprehensive statistics."""
        try:
            with self.get_session() as session:
                total_opportunities = session.query(OpportunityDB).count()
                
                # Country statistics
                countries_data = session.query(OpportunityDB.looking_for_participants_from).all()
                countries_stats = {}
                for country_data in countries_data:
                    if country_data[0]:
                        countries = [c.strip() for c in country_data[0].split(',')]
                        for country in countries:
                            if country:
                                countries_stats[country] = countries_stats.get(country, 0) + 1
                
                # Topics statistics
                topics_data = session.query(OpportunityDB.activity_topics).all()
                topics_stats = {}
                for topic_data in topics_data:
                    if topic_data[0]:
                        topics = [t.strip() for t in topic_data[0].split(',')]
                        for topic in topics:
                            if topic:
                                topics_stats[topic] = topics_stats.get(topic, 0) + 1
                
                # Location statistics
                locations_data = session.query(OpportunityDB.activity_location).all()
                locations_stats = {}
                for location_data in locations_data:
                    if location_data[0]:
                        location = location_data[0].strip()
                        if location:
                            locations_stats[location] = locations_stats.get(location, 0) + 1
                
                # Recent additions (last 7 days)
                week_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                week_ago = week_ago.replace(day=week_ago.day - 7)
                recent_additions = session.query(OpportunityDB).filter(
                    OpportunityDB.scraped_at >= week_ago
                ).count()
                
                return Statistics(
                    total_opportunities=total_opportunities,
                    countries_stats=dict(sorted(countries_stats.items(), key=lambda x: x[1], reverse=True)),
                    topics_stats=dict(sorted(topics_stats.items(), key=lambda x: x[1], reverse=True)),
                    locations_stats=dict(sorted(locations_stats.items(), key=lambda x: x[1], reverse=True)),
                    recent_additions=recent_additions,
                    last_update=datetime.now()
                )
        
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return Statistics(
                total_opportunities=0,
                countries_stats={},
                topics_stats={},
                locations_stats={},
                recent_additions=0,
                last_update=datetime.now()
            )
    
    def export_to_pandas(self, filters: QueryFilter = None) -> pd.DataFrame:
        """Export data to pandas DataFrame for advanced analysis."""
        try:
            if filters:
                result = self.query_opportunities(filters)
                opportunities = result.opportunities
            else:
                with self.get_session() as session:
                    results = session.query(OpportunityDB).all()
                    opportunities = []
                    for result in results:
                        opportunity_dict = {
                            column.name: getattr(result, column.name) 
                            for column in result.__table__.columns
                        }
                        opportunities.append(OpportunityDetail(**opportunity_dict))
            
            # Convert to DataFrame
            data = [opportunity.dict() for opportunity in opportunities]
            df = pd.DataFrame(data)
            
            return df
        
        except Exception as e:
            logger.error(f"Pandas export error: {e}")
            return pd.DataFrame()
    
    def backup_to_json(self, file_path: str = None):
        """Backup database to JSON file."""
        file_path = file_path or database_config.json_backup_path
        try:
            df = self.export_to_pandas()
            if not df.empty:
                # Convert datetime columns to strings for JSON serialization
                for col in df.select_dtypes(include=['datetime64']).columns:
                    df[col] = df[col].astype(str)
                
                data = df.to_dict('records')
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Database backed up to {file_path}")
                return True
        
        except Exception as e:
            logger.error(f"Backup error: {e}")
            return False
    
    def get_opportunity_by_id(self, opid: str) -> Optional[OpportunityDetail]:
        """Get a specific opportunity by ID."""
        try:
            with self.get_session() as session:
                result = session.query(OpportunityDB).filter_by(opid=opid).first()
                if result:
                    opportunity_dict = {
                        column.name: getattr(result, column.name) 
                        for column in result.__table__.columns
                    }
                    return OpportunityDetail(**opportunity_dict)
                return None
        
        except Exception as e:
            logger.error(f"Error getting opportunity {opid}: {e}")
            return None 