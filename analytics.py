"""
Advanced analytics and visualization module for opportunity data.
Provides insights, trends analysis, and interactive visualizations.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from database import DatabaseManager
from models import OpportunityDetail, QueryFilter

logger = logging.getLogger(__name__)


class OpportunityAnalytics:
    """Advanced analytics engine for opportunity data."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize analytics engine."""
        self.db_manager = db_manager
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """Load data into pandas DataFrame for analysis."""
        try:
            self.df = self.db_manager.export_to_pandas()
            if not self.df.empty:
                # Data preprocessing
                self.df['scraped_at'] = pd.to_datetime(self.df['scraped_at'])
                self.df['last_updated'] = pd.to_datetime(self.df['last_updated'])
                self._preprocess_data()
                logger.info(f"Loaded {len(self.df)} opportunities for analysis")
            else:
                logger.warning("No data available for analysis")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def _preprocess_data(self):
        """Preprocess data for better analysis."""
        if self.df.empty:
            return
        
        # Clean and expand country data
        self.df['country_count'] = self.df['participant_countries'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        
        # Clean and expand topic data
        self.df['topic_count'] = self.df['topics_list'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        
        # Extract location countries/regions
        self.df['location_country'] = self.df['activity_location'].apply(
            self._extract_location_country
        )
        
        # Text length analysis
        self.df['description_length'] = self.df['description'].fillna('').str.len()
        self.df['title_length'] = self.df['title'].str.len()
        
        # Date analysis
        self.df['days_since_scraped'] = (
            datetime.now() - self.df['scraped_at']
        ).dt.days
    
    def _extract_location_country(self, location: str) -> str:
        """Extract country from location string."""
        if not isinstance(location, str):
            return "Unknown"
        
        # Simple country extraction (can be improved with geopy)
        common_countries = [
            'Germany', 'France', 'Italy', 'Spain', 'Poland', 'Netherlands',
            'Belgium', 'Czech Republic', 'Austria', 'Hungary', 'Portugal',
            'Sweden', 'Denmark', 'Finland', 'Norway', 'Ireland', 'Greece',
            'Croatia', 'Slovenia', 'Slovakia', 'Romania', 'Bulgaria',
            'Lithuania', 'Latvia', 'Estonia', 'Cyprus', 'Malta', 'Luxembourg'
        ]
        
        location_upper = location.upper()
        for country in common_countries:
            if country.upper() in location_upper:
                return country
        
        return "Other"
    
    def generate_country_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive country-based analysis."""
        if self.df.empty:
            return {}
        
        analysis = {}
        
        # Country participation frequency
        all_countries = []
        for countries in self.df['participant_countries'].dropna():
            if isinstance(countries, list):
                all_countries.extend(countries)
        
        country_freq = Counter(all_countries)
        analysis['country_frequency'] = dict(country_freq.most_common(20))
        
        # Location distribution
        location_dist = self.df['location_country'].value_counts().to_dict()
        analysis['location_distribution'] = location_dist
        
        # Average opportunities per country
        analysis['avg_opportunities_per_country'] = len(all_countries) / len(country_freq) if country_freq else 0
        
        # Top country pairs (countries often mentioned together)
        country_pairs = []
        for countries in self.df['participant_countries'].dropna():
            if isinstance(countries, list) and len(countries) > 1:
                for i in range(len(countries)):
                    for j in range(i+1, len(countries)):
                        pair = tuple(sorted([countries[i], countries[j]]))
                        country_pairs.append(pair)
        
        pair_freq = Counter(country_pairs)
        analysis['country_pairs'] = dict(pair_freq.most_common(10))
        
        return analysis
    
    def generate_topic_analysis(self) -> Dict[str, Any]:
        """Generate topic-based analysis and trends."""
        if self.df.empty:
            return {}
        
        analysis = {}
        
        # Topic frequency
        all_topics = []
        for topics in self.df['topics_list'].dropna():
            if isinstance(topics, list):
                all_topics.extend(topics)
        
        topic_freq = Counter(all_topics)
        analysis['topic_frequency'] = dict(topic_freq.most_common(20))
        
        # Topic co-occurrence
        topic_pairs = []
        for topics in self.df['topics_list'].dropna():
            if isinstance(topics, list) and len(topics) > 1:
                for i in range(len(topics)):
                    for j in range(i+1, len(topics)):
                        pair = tuple(sorted([topics[i], topics[j]]))
                        topic_pairs.append(pair)
        
        pair_freq = Counter(topic_pairs)
        analysis['topic_pairs'] = dict(pair_freq.most_common(10))
        
        # Average topics per opportunity
        analysis['avg_topics_per_opportunity'] = self.df['topic_count'].mean()
        
        return analysis
    
    def generate_temporal_analysis(self) -> Dict[str, Any]:
        """Generate time-based analysis and trends."""
        if self.df.empty:
            return {}
        
        analysis = {}
        
        # Scraping timeline
        daily_counts = self.df.groupby(self.df['scraped_at'].dt.date).size()
        analysis['daily_scraping_counts'] = daily_counts.to_dict()
        
        # Recent activity (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_opportunities = self.df[self.df['scraped_at'] >= recent_cutoff]
        analysis['recent_opportunities_count'] = len(recent_opportunities)
        
        # Growth trend
        if len(daily_counts) > 1:
            recent_avg = daily_counts.tail(7).mean()  # Last week average
            overall_avg = daily_counts.mean()
            analysis['growth_trend'] = (recent_avg - overall_avg) / overall_avg * 100 if overall_avg > 0 else 0
        else:
            analysis['growth_trend'] = 0
        
        return analysis
    
    def generate_content_analysis(self) -> Dict[str, Any]:
        """Analyze content patterns and quality metrics."""
        if self.df.empty:
            return {}
        
        analysis = {}
        
        # Description length statistics
        desc_stats = self.df['description_length'].describe()
        analysis['description_length_stats'] = desc_stats.to_dict()
        
        # Title length statistics
        title_stats = self.df['title_length'].describe()
        analysis['title_length_stats'] = title_stats.to_dict()
        
        # Common words in descriptions (simple analysis)
        all_descriptions = ' '.join(self.df['description'].fillna('').astype(str))
        word_freq = Counter(re.findall(r'\b\w+\b', all_descriptions.lower()))
        # Filter out common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        filtered_words = {word: count for word, count in word_freq.items() 
                         if len(word) > 3 and word not in stop_words}
        analysis['common_words'] = dict(Counter(filtered_words).most_common(20))
        
        # Data completeness
        completeness = {}
        for col in ['description', 'activity_location', 'participant_profile', 'activity_topics']:
            non_null_count = self.df[col].notna().sum()
            completeness[col] = (non_null_count / len(self.df)) * 100
        analysis['data_completeness'] = completeness
        
        return analysis
    
    def create_country_visualization(self, save_path: str = None) -> go.Figure:
        """Create interactive country distribution visualization."""
        country_analysis = self.generate_country_analysis()
        
        if not country_analysis.get('country_frequency'):
            return go.Figure()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Top Countries for Participants',
                'Activity Locations',
                'Country Co-occurrence Network',
                'Geographic Distribution'
            ),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Top countries bar chart
        countries = list(country_analysis['country_frequency'].keys())[:15]
        counts = list(country_analysis['country_frequency'].values())[:15]
        
        fig.add_trace(
            go.Bar(x=countries, y=counts, name="Participant Opportunities"),
            row=1, col=1
        )
        
        # Location distribution pie chart
        locations = list(country_analysis['location_distribution'].keys())[:10]
        location_counts = list(country_analysis['location_distribution'].values())[:10]
        
        fig.add_trace(
            go.Pie(labels=locations, values=location_counts, name="Locations"),
            row=1, col=2
        )
        
        # Country pairs network (simplified as bar chart)
        if country_analysis.get('country_pairs'):
            pairs = list(country_analysis['country_pairs'].keys())[:10]
            pair_counts = list(country_analysis['country_pairs'].values())[:10]
            pair_labels = [f"{p[0]} - {p[1]}" for p in pairs]
            
            fig.add_trace(
                go.Bar(x=pair_labels, y=pair_counts, name="Country Pairs"),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title_text="European Youth Opportunities - Country Analysis",
            showlegend=True,
            height=800
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_topic_visualization(self, save_path: str = None) -> go.Figure:
        """Create interactive topic analysis visualization."""
        topic_analysis = self.generate_topic_analysis()
        
        if not topic_analysis.get('topic_frequency'):
            return go.Figure()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Most Popular Topics',
                'Topic Distribution',
                'Topic Co-occurrence',
                'Topics per Opportunity'
            ),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # Top topics bar chart
        topics = list(topic_analysis['topic_frequency'].keys())[:15]
        topic_counts = list(topic_analysis['topic_frequency'].values())[:15]
        
        fig.add_trace(
            go.Bar(x=topics, y=topic_counts, name="Topic Frequency"),
            row=1, col=1
        )
        
        # Topic distribution pie chart (top 10)
        fig.add_trace(
            go.Pie(labels=topics[:10], values=topic_counts[:10], name="Topic Distribution"),
            row=1, col=2
        )
        
        # Topic pairs
        if topic_analysis.get('topic_pairs'):
            pairs = list(topic_analysis['topic_pairs'].keys())[:10]
            pair_counts = list(topic_analysis['topic_pairs'].values())[:10]
            pair_labels = [f"{p[0]} + {p[1]}" for p in pairs]
            
            fig.add_trace(
                go.Bar(x=pair_labels, y=pair_counts, name="Topic Pairs"),
                row=2, col=1
            )
        
        # Topics per opportunity histogram
        if not self.df.empty:
            fig.add_trace(
                go.Histogram(x=self.df['topic_count'], name="Topics per Opportunity"),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="European Youth Opportunities - Topic Analysis",
            showlegend=True,
            height=800
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_temporal_visualization(self, save_path: str = None) -> go.Figure:
        """Create temporal trends visualization."""
        temporal_analysis = self.generate_temporal_analysis()
        
        if not temporal_analysis.get('daily_scraping_counts'):
            return go.Figure()
        
        # Convert to DataFrame for easier plotting
        dates = list(temporal_analysis['daily_scraping_counts'].keys())
        counts = list(temporal_analysis['daily_scraping_counts'].values())
        
        fig = go.Figure()
        
        # Line chart for daily trends
        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='Daily Opportunities',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        # Add trend line
        if len(dates) > 1:
            import numpy as np
            x_numeric = np.arange(len(dates))
            z = np.polyfit(x_numeric, counts, 1)
            p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=p(x_numeric),
                mode='lines',
                name='Trend',
                line=dict(color='red', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Opportunity Discovery Timeline",
            xaxis_title="Date",
            yaxis_title="Number of Opportunities",
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        if self.df.empty:
            return {"error": "No data available for analysis"}
        
        insights = {
            "overview": {
                "total_opportunities": len(self.df),
                "unique_countries": len(set().union(*self.df['participant_countries'].dropna())),
                "unique_topics": len(set().union(*self.df['topics_list'].dropna())),
                "avg_countries_per_opportunity": self.df['country_count'].mean(),
                "avg_topics_per_opportunity": self.df['topic_count'].mean(),
            },
            "country_analysis": self.generate_country_analysis(),
            "topic_analysis": self.generate_topic_analysis(),
            "temporal_analysis": self.generate_temporal_analysis(),
            "content_analysis": self.generate_content_analysis(),
            "recommendations": self._generate_recommendations()
        }
        
        return insights
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on data analysis."""
        recommendations = []
        
        if self.df.empty:
            return ["No data available for recommendations"]
        
        # Country diversity
        unique_countries = len(set().union(*self.df['participant_countries'].dropna()))
        if unique_countries < 10:
            recommendations.append(
                f"Consider expanding to more countries. Currently only {unique_countries} countries are represented."
            )
        
        # Topic diversity
        unique_topics = len(set().union(*self.df['topics_list'].dropna()))
        if unique_topics < 15:
            recommendations.append(
                f"Topic diversity could be improved. Currently {unique_topics} unique topics are covered."
            )
        
        # Data completeness
        content_analysis = self.generate_content_analysis()
        completeness = content_analysis.get('data_completeness', {})
        for field, percentage in completeness.items():
            if percentage < 80:
                recommendations.append(
                    f"Improve data quality for {field}: only {percentage:.1f}% complete"
                )
        
        # Recent activity
        temporal_analysis = self.generate_temporal_analysis()
        growth_trend = temporal_analysis.get('growth_trend', 0)
        if growth_trend < 0:
            recommendations.append(
                f"Opportunity discovery rate is declining ({growth_trend:.1f}%). Consider updating scraping strategies."
            )
        
        return recommendations
    
    def export_analytics_report(self, file_path: str):
        """Export comprehensive analytics report to JSON."""
        report = self.generate_insights_report()
        
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Analytics report exported to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting analytics report: {e}")
            return False 