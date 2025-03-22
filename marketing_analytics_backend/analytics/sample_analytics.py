"""
Analytics tasks for processing sample data and generating insights.
"""
import logging
import os
import json
from datetime import datetime, timedelta
from database.supabase_client import SupabaseClient
from gemini_integration.client import GeminiClient
from gemini_integration.video_analysis import GeminiVideoAnalyzer
from sample_data.processor import process_sample_videos

logger = logging.getLogger(__name__)

class SampleAnalyticsProcessor:
    """Processor for running analytics on sample data."""
    
    def __init__(self, gemini_api_key):
        """
        Initialize the analytics processor.
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        self.supabase = SupabaseClient()
        self.gemini_client = GeminiClient(gemini_api_key)
        self.video_analyzer = GeminiVideoAnalyzer(gemini_api_key)
    
    def run_analytics_for_business(self, business_id, sample_videos_dir=None, temp_dir=None):
        """
        Run analytics for a specific business using sample data.
        
        Args:
            business_id: ID of the business to analyze
            sample_videos_dir: Directory containing sample videos (optional)
            temp_dir: Directory for temporary files (optional)
            
        Returns:
            List of generated insights
        """
        # Get business
        business = self.supabase.get_business(business_id)
        if not business:
            logger.error(f"Business with ID {business_id} not found")
            return []
        
        logger.info(f"Running analytics for business: {business['name']}")
        
        # Get social accounts for the business
        accounts = self.supabase.get_social_accounts(business_id)
        if not accounts:
            logger.warning(f"No social accounts found for business {business['name']}")
            return []
        
        # Get account IDs
        account_ids = [account['id'] for account in accounts]
        
        # Get metrics for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get metrics for the accounts
        metrics = []
        for account_id in account_ids:
            account_metrics = self.supabase.get_metrics(
                account_id=account_id,
                start_date=start_date,
                end_date=end_date
            )
            metrics.extend(account_metrics)
        
        # Get content for the accounts
        content_items = []
        for account_id in account_ids:
            account_content = self.supabase.get_content(
                account_id=account_id,
                start_date=start_date,
                end_date=end_date
            )
            content_items.extend(account_content)
            
            # Process video content if sample videos directory is provided
            video_analysis_results = []
            if sample_videos_dir and temp_dir and os.path.exists(sample_videos_dir):
                # Process sample videos
                video_data = process_sample_videos(sample_videos_dir, temp_dir)
                
                # Prepare content info for video analysis
                content_info = {}
                for item in content_items:
                    if item['content_type'] in ['video', 'reel', 'short']:
                        account = next((a for a in accounts if a['id'] == item['social_account_id']), None)
                        if account:
                            content_info[item['id']] = {
                                'content_id': item['content_id'],
                                'platform': account['platform'],
                                'content_type': item['content_type'],
                                'title': item['title'],
                                'description': item['description']
                            }
                
                # Analyze videos
                if video_data and content_info:
                    video_analysis_results = self.video_analyzer.analyze_video_batch(
                        video_data, content_info
                    )
            
            # Generate insights
            insights = self._generate_insights(
                business, accounts, metrics, content_items, video_analysis_results
            )
            
            return insights
    
    def _generate_insights(self, business, accounts, metrics, content_items, video_analysis_results):
        """
        Generate insights for a business based on analytics data.
        
        Args:
            business: Business dictionary from Supabase
            accounts: List of SocialAccount dictionaries
            metrics: List of SocialMetric dictionaries
            content_items: List of Content dictionaries
            video_analysis_results: List of video analysis results
            
        Returns:
            List of generated insights
        """
        insights = []
        
        # Prepare data for Gemini
        business_data = {
            'id': business['id'],
            'name': business['name'],
            'industry': business['industry']
        }
        
        accounts_data = []
        for account in accounts:
            accounts_data.append({
                'id': account['id'],
                'platform': account['platform'],
                'account_name': account['account_name']
            })
        
        metrics_data = []
        for metric in metrics:
            # Parse platform_data from JSON string if needed
            platform_data = metric['platform_data']
            if isinstance(platform_data, str):
                try:
                    platform_data = json.loads(platform_data)
                except:
                    platform_data = {}
            
            metrics_data.append({
                'social_account_id': metric['social_account_id'],
                'timestamp': metric['timestamp'],
                'followers': metric['followers'],
                'likes': metric['likes'],
                'comments': metric['comments'],
                'shares': metric['shares'],
                'views': metric['views'],
                'platform_data': platform_data
            })
        
        content_data = []
        for item in content_items:
            # Parse content_metadata from JSON string if needed
            content_metadata = item['content_metadata']
            if isinstance(content_metadata, str):
                try:
                    content_metadata = json.loads(content_metadata)
                except:
                    content_metadata = {}
            
            content_data.append({
                'id': item['id'],
                'social_account_id': item['social_account_id'],
                'content_type': item['content_type'],
                'title': item['title'],
                'description': item['description'],
                'published_at': item['published_at'],
                'likes': item['likes'],
                'comments': item['comments'],
                'shares': item['shares'],
                'views': item['views'],
                'metadata': content_metadata
            })
        
        # Generate engagement insights
        engagement_insights = self.gemini_client.analyze_engagement_trends(
            business_data, accounts_data, metrics_data, content_data
        )
        
        if engagement_insights:
            for insight_data in engagement_insights:
                insight_data = {
                    'business_id': business['id'],
                    'insight_type': 'engagement',
                    'title': insight_data.get('title', 'Engagement Insight'),
                    'content': insight_data.get('content', ''),
                    'timestamp': datetime.now().isoformat()
                }
                insights.append(insight_data)
                # Save to Supabase
                self.supabase.create_insight(
                    business_id=business['id'],
                    insight_type='engagement',
                    title=insight_data['title'],
                    content=insight_data['content']
                )
        
        # Generate content insights
        content_insights = self.gemini_client.analyze_content_performance(
            business_data, accounts_data, content_data
        )
        
        if content_insights:
            for insight_data in content_insights:
                insight_data = {
                    'business_id': business['id'],
                    'insight_type': 'content',
                    'title': insight_data.get('title', 'Content Insight'),
                    'content': insight_data.get('content', ''),
                    'timestamp': datetime.now().isoformat()
                }
                insights.append(insight_data)
                # Save to Supabase
                self.supabase.create_insight(
                    business_id=business['id'],
                    insight_type='content',
                    title=insight_data['title'],
                    content=insight_data['content']
                )
        
        # Generate video-specific insights
        if video_analysis_results:
            video_insights = self.gemini_client.analyze_video_content_results(
                business_data, video_analysis_results
            )
            
            if video_insights:
                for insight_data in video_insights:
                    insight_data = {
                        'business_id': business['id'],
                        'insight_type': 'video',
                        'title': insight_data.get('title', 'Video Content Insight'),
                        'content': insight_data.get('content', ''),
                        'timestamp': datetime.now().isoformat()
                    }
                    insights.append(insight_data)
                    # Save to Supabase
                    self.supabase.create_insight(
                        business_id=business['id'],
                        insight_type='video',
                        title=insight_data['title'],
                        content=insight_data['content']
                    )
        
        # Generate product demand insights
        product_insights = self.gemini_client.analyze_product_demand(
            business_data, accounts_data, content_data
        )
        
        if product_insights:
            for insight_data in product_insights:
                insight_data = {
                    'business_id': business['id'],
                    'insight_type': 'product',
                    'title': insight_data.get('title', 'Product Demand Insight'),
                    'content': insight_data.get('content', ''),
                    'timestamp': datetime.now().isoformat()
                }
                insights.append(insight_data)
                # Save to Supabase
                self.supabase.create_insight(
                    business_id=business['id'],
                    insight_type='product',
                    title=insight_data['title'],
                    content=insight_data['content']
                )
        
        return insights
