"""
Professional web scraper for the European Youth Portal.
Features async operations, advanced error handling, and monitoring.
"""

import asyncio
import aiohttp
import logging
import random
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from asyncio_throttle import Throttler
import time

from models import OpportunityDetail, ScrapingSession
from config import scraping_config, USER_AGENTS, API_PARAMS, SECTION_MAPPINGS
from database import DatabaseManager

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    """Custom exception for scraping errors."""
    pass


class RateLimitError(ScrapingError):
    """Exception for rate limiting issues."""
    pass


class ProfessionalScraper:
    """Professional web scraper with advanced features."""
    
    def __init__(self, db_manager: DatabaseManager, progress_callback=None):
        """Initialize the professional scraper."""
        self.db_manager = db_manager
        self.config = scraping_config
        self.session_id = str(uuid.uuid4())
        self.session_data = ScrapingSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Progress callback for real-time updates
        self.progress_callback = progress_callback
        
        # Rate limiting - Conservative for reliability
        self.throttler = Throttler(rate_limit=3, period=1.0)
        
        logger.info(f"Professional scraper initialized - Session: {self.session_id}")
    
    async def _get_session_with_retry(self) -> aiohttp.ClientSession:
        """Create aiohttp session with retry configuration."""
        connector = aiohttp.TCPConnector(
            limit=self.config.max_workers * 2,  # More connections
            limit_per_host=self.config.max_workers,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True,  # Auto cleanup
            keepalive_timeout=30,  # Keep connections alive longer
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': random.choice(USER_AGENTS)}
        )
    
    async def _make_request_with_retry(self, session: aiohttp.ClientSession, 
                                     url: str, params: Dict = None) -> Optional[str]:
        """Make HTTP request with retry logic and rate limiting."""
        for attempt in range(self.config.max_retries):
            try:
                async with self.throttler:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:  # Rate limited
                            # Exponential backoff for rate limiting
                            wait_time = min(60, (3 ** attempt) * self.config.retry_delay)
                            logger.warning(f"Rate limited (429). Waiting {wait_time}s before retry {attempt + 1}/{self.config.max_retries}")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            return None
            
            except asyncio.TimeoutError:
                wait_time = (2 ** attempt) * self.config.retry_delay
                logger.warning(f"Timeout for {url}. Retry {attempt + 1} after {wait_time}s")
                await asyncio.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"Request error for {url}: {e}")
                if attempt == self.config.max_retries - 1:
                    return None
                await asyncio.sleep(self.config.retry_delay)
        
        return None
    
    async def get_all_opportunities_summary(self) -> List[Dict[str, Any]]:
        """Fetch all opportunities summary using async pagination."""
        all_opportunities = []
        current_from = 0
        
        logger.info("Starting async pagination for opportunities summary")
        
        async with await self._get_session_with_retry() as session:
            while True:
                params = API_PARAMS.copy()
                params.update({
                    'from': current_from,
                    'size': self.config.page_size
                })
                
                try:
                    response_text = await self._make_request_with_retry(
                        session, self.config.base_url, params
                    )
                    
                    if not response_text:
                        logger.error(f"Failed to get response for page from={current_from}")
                        break
                    
                    data = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: __import__('json').loads(response_text)
                    )
                    
                    opportunity_batch = data.get('hits', {}).get('hits', [])
                    
                    if not opportunity_batch:
                        logger.info("No more opportunities found. Pagination complete.")
                        break
                    
                    all_opportunities.extend(opportunity_batch)
                    current_from += self.config.page_size
                    
                    logger.info(f"Fetched {len(opportunity_batch)} items. Total: {len(all_opportunities)}")
                    
                except Exception as e:
                    logger.error(f"Error during pagination at from={current_from}: {e}")
                    self.session_data.errors.append(f"Pagination error: {e}")
                    break
        
        self.session_data.total_opportunities_found = len(all_opportunities)
        logger.info(f"Pagination complete. Found {len(all_opportunities)} opportunities.")
        return all_opportunities
    
    async def fetch_opportunity_details(self, session: aiohttp.ClientSession, 
                                      summary: Dict[str, Any]) -> Optional[OpportunityDetail]:
        """Fetch detailed information for a single opportunity."""
        source = summary.get('_source', {})
        opid = source.get('opid')
        
        if not opid:
            logger.warning("No opid found in summary")
            return None
        
        detail_url = self.config.detail_url_template.format(opid=opid)
        
        try:
            response_text = await self._make_request_with_retry(session, detail_url)
            
            if not response_text:
                logger.warning(f"Failed to fetch details for opportunity {opid}")
                return None
            
            # Parse HTML in executor with faster parser
            soup = await asyncio.get_event_loop().run_in_executor(
                None, lambda: BeautifulSoup(response_text, 'lxml')
            )
            
            # Extract structured data
            structured_data = {
                "opid": opid,
                "url": detail_url,
                "title": self._extract_title(soup, source)
            }
            
            # Extract sections
            for section_name, json_key in SECTION_MAPPINGS.items():
                content = self._extract_section_content(soup, section_name)
                structured_data[json_key] = content
            
            # Create and validate the opportunity model
            opportunity = OpportunityDetail(**structured_data)
            
            self.session_data.successful_scrapes += 1
            logger.debug(f"Successfully scraped opportunity {opid}")
            return opportunity
        
        except Exception as e:
            self.session_data.failed_scrapes += 1
            error_msg = f"Error scraping opportunity {opid}: {e}"
            logger.error(error_msg)
            self.session_data.errors.append(error_msg)
            return None
    
    def _extract_title(self, soup: BeautifulSoup, source: Dict[str, Any]) -> str:
        """Extract title from soup or fallback to source."""
        title_element = soup.find('h1', class_='od-title')
        if title_element:
            return title_element.get_text(strip=True)
        return source.get('title', 'N/A')
    
    def _extract_section_content(self, soup: BeautifulSoup, section_name: str) -> str:
        """Extract content for a specific section."""
        headings = soup.find_all('h6')
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if heading_text == section_name:
                next_p = heading.find_next('p')
                if next_p:
                    return next_p.get_text(strip=True, separator='\n')
        return "N/A"
    
    async def scrape_all_opportunities_async(self, opportunities_summary: List[Dict[str, Any]]) -> List[OpportunityDetail]:
        """Scrape all opportunity details using async/await."""
        if not opportunities_summary:
            logger.warning("No opportunities to scrape")
            return []
        
        logger.info(f"Starting async scraping for {len(opportunities_summary)} opportunities")
        
        all_opportunities = []
        
        async with await self._get_session_with_retry() as session:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(self.config.max_workers)
            
            async def scrape_with_semaphore(summary):
                async with semaphore:
                    return await self.fetch_opportunity_details(session, summary)
            
            # Create tasks for all opportunities
            tasks = [scrape_with_semaphore(summary) for summary in opportunities_summary]
            
            # Process tasks with progress tracking
            completed = 0
            total = len(tasks)
            
            for coro in asyncio.as_completed(tasks):
                result = await coro
                completed += 1
                
                if result:
                    all_opportunities.append(result)
                
                # Update progress callback for real-time UI updates
                if self.progress_callback:
                    percentage = (completed / total) * 100
                    self.progress_callback(completed, total, percentage, len(all_opportunities))
                
                # Log progress every 10% or every 100 items
                if completed % max(1, total // 10) == 0 or completed % 100 == 0:
                    percentage = (completed / total) * 100
                    logger.info(f"Progress: {completed}/{total} ({percentage:.1f}%) - "
                              f"Success: {len(all_opportunities)}")
        
        # Update session data
        self.session_data.end_time = datetime.now()
        self.session_data.status = "completed"
        
        duration = (self.session_data.end_time - self.session_data.start_time).total_seconds()
        logger.info(f"Async scraping completed in {duration:.2f}s. "
                   f"Scraped {len(all_opportunities)} opportunities successfully.")
        
        return all_opportunities
    
    async def run_full_scraping_pipeline(self) -> int:
        """Run the complete scraping pipeline with retry for failed items."""
        try:
            logger.info("Starting full scraping pipeline")
            
            # Step 1: Get opportunities summary
            summaries = await self.get_all_opportunities_summary()
            if not summaries:
                logger.warning("No opportunities found in summary")
                return 0
            
            # Step 2: Scrape detailed information (first pass)
            opportunities = await self.scrape_all_opportunities_async(summaries)
            
            # Step 3: Retry failed items for better success rate
            if self.session_data.failed_scrapes > 0:
                logger.info(f"Retrying {self.session_data.failed_scrapes} failed items...")
                failed_summaries = [s for s in summaries if s.get('_source', {}).get('opid') not in [op.opid for op in opportunities]]
                
                if failed_summaries:
                    # Reset counters for retry
                    retry_failed = self.session_data.failed_scrapes
                    self.session_data.failed_scrapes = 0
                    
                    # Wait before retry
                    await asyncio.sleep(5)
                    
                    # Retry with more conservative settings
                    old_throttler = self.throttler
                    self.throttler = Throttler(rate_limit=1, period=2.0)  # Very conservative
                    
                    retry_opportunities = await self.scrape_all_opportunities_async(failed_summaries)
                    opportunities.extend(retry_opportunities)
                    
                    # Restore throttler
                    self.throttler = old_throttler
                    
                    logger.info(f"Retry completed. Recovered {len(retry_opportunities)} additional opportunities.")
            
            if not opportunities:
                logger.warning("No opportunities scraped successfully")
                return 0
            
            # Step 4: Save to database
            logger.info(f"Saving {len(opportunities)} opportunities to database")
            saved_count = self.db_manager.bulk_insert_opportunities(opportunities)
            
            # Step 5: Backup to JSON if configured
            from config import database_config
            if database_config.auto_backup:
                self.db_manager.backup_to_json()
            
            logger.info(f"Scraping pipeline completed. Saved {saved_count} opportunities.")
            return saved_count
        
        except Exception as e:
            self.session_data.status = "failed"
            self.session_data.end_time = datetime.now()
            error_msg = f"Scraping pipeline failed: {e}"
            logger.error(error_msg)
            self.session_data.errors.append(error_msg)
            return 0
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics for the current scraping session."""
        duration = None
        if self.session_data.end_time:
            duration = (self.session_data.end_time - self.session_data.start_time).total_seconds()
        
        return {
            "session_id": self.session_data.session_id,
            "start_time": self.session_data.start_time,
            "end_time": self.session_data.end_time,
            "duration_seconds": duration,
            "status": self.session_data.status,
            "total_found": self.session_data.total_opportunities_found,
            "successful_scrapes": self.session_data.successful_scrapes,
            "failed_scrapes": self.session_data.failed_scrapes,
            "success_rate": (
                self.session_data.successful_scrapes / 
                max(1, self.session_data.total_opportunities_found)
            ) * 100,
            "errors_count": len(self.session_data.errors),
            "errors": self.session_data.errors[-10:]  # Last 10 errors
        } 