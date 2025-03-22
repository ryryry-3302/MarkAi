"""
Analytics tasks for generating insights from social media data.
"""
import logging
from datetime import datetime, timedelta
from flask import current_app
from database.models import db, Business, SocialAccount, SocialMetric, Content, Insight
from gemini_integration.client import GeminiClient

logger = logging.getLogger(__name__)

def run_analytics():
    """Run analytics tasks to generate insights for all businesses."""
    logger.info("Starting analytics tasks")
    
    try:
        # Get Gemini API key from config
        gemini_api_key = current_app.config.get('GEMINI_API_KEY')
        
        if not gemini_api_key:
            logger.error("Gemini API key not configured")
            return
        
        # Initialize Gemini client
        gemini_client = GeminiClient(gemini_api_key)
        
        # Get all businesses from database
        businesses = Business.query.all()
        
        for business in businesses:
            try:
                logger.info(f"Generating insights for business: {business.name}")
                
                # Generate insights for the business
                generate_business_insights(business, gemini_client)
                
                logger.info(f"Successfully generated insights for business: {business.name}")
                
            except Exception as e:
                logger.error(f"Error generating insights for business {business.name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in analytics task: {str(e)}")

def generate_business_insights(business, gemini_client):
    """Generate insights for a specific business."""
    # Get all social accounts for the business
    social_accounts = SocialAccount.query.filter_by(business_id=business.id).all()
    
    if not social_accounts:
        logger.warning(f"No social accounts found for business: {business.name}")
        return
    
    # Define time period for analysis (last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Collect metrics and content data for all platforms
    metrics_data = []
    content_data = []
    
    for account in social_accounts:
        # Get metrics for the account
        metrics = SocialMetric.query.filter(
            SocialMetric.social_account_id == account.id,
            SocialMetric.timestamp >= start_date,
            SocialMetric.timestamp <= end_date
        ).order_by(SocialMetric.timestamp).all()
        
        # Get content for the account
        content = Content.query.filter(
            Content.social_account_id == account.id,
            Content.published_at >= start_date,
            Content.published_at <= end_date
        ).order_by(Content.published_at.desc()).all()
        
        # Format metrics data
        for metric in metrics:
            metric_data = {
                'platform': account.platform,
                'account_name': account.account_name,
                'timestamp': metric.timestamp.isoformat(),
                'followers': metric.followers,
                'likes': metric.likes,
                'comments': metric.comments,
                'shares': metric.shares,
                'views': metric.views,
                'platform_data': metric.get_platform_data()
            }
            metrics_data.append(metric_data)
        
        # Format content data
        for item in content:
            content_item = {
                'platform': account.platform,
                'account_name': account.account_name,
                'content_id': item.content_id,
                'content_type': item.content_type,
                'title': item.title,
                'description': item.description,
                'url': item.url,
                'published_at': item.published_at.isoformat(),
                'likes': item.likes,
                'comments': item.comments,
                'shares': item.shares,
                'views': item.views,
                'metadata': item.get_content_metadata()
            }
            content_data.append(content_item)
    
    # Generate engagement trend insights
    engagement_insights = gemini_client.analyze_engagement_trends(metrics_data, content_data, business.name)
    
    # Save engagement insights to database
    save_insight(business.id, 'engagement_trends', engagement_insights)
    
    # Generate product demand insights
    product_insights = gemini_client.analyze_product_demand(content_data, business.name, business.industry)
    
    # Save product insights to database
    save_insight(business.id, 'product_demand', product_insights)
    
    # Get all insights for the business to generate recommendations
    all_insights = [engagement_insights, product_insights]
    
    # Generate marketing recommendations
    recommendations = gemini_client.generate_marketing_recommendations(all_insights, business.name, business.industry)
    
    # Save recommendations to database
    save_insight(business.id, 'marketing_recommendations', recommendations)

def save_insight(business_id, insight_type, insight_data):
    """Save an insight to the database."""
    try:
        # Create new Insight record
        insight = Insight(
            business_id=business_id,
            insight_type=insight_type,
            title=insight_data.get('title', f'{insight_type.replace("_", " ").title()} Insight'),
            description=str(insight_data.get('insights', insight_data.get('recommendations', {}))),
            confidence_score=insight_data.get('confidence_score', 0.7),
            generated_at=datetime.utcnow()
        )
        
        # Store raw data
        insight.set_raw_data(insight_data)
        
        db.session.add(insight)
        db.session.commit()
        
        logger.info(f"Saved {insight_type} insight for business ID {business_id}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving insight: {str(e)}")
        raise
