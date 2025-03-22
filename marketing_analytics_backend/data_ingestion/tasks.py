"""
Data ingestion tasks for fetching data from social media platforms.
Contains functions for fetching data from Instagram, YouTube, and TikTok.
"""
import logging
from datetime import datetime
from flask import current_app
from database.models import db, SocialAccount, SocialMetric, Content
from .platforms.instagram import InstagramClient
from .platforms.youtube import YouTubeClient
from .platforms.tiktok import TikTokClient

logger = logging.getLogger(__name__)

def fetch_instagram_data():
    """Fetch data from Instagram for all registered business accounts."""
    logger.info("Starting Instagram data fetch")
    
    try:
        # Get Instagram API credentials from config
        api_key = current_app.config.get('INSTAGRAM_API_KEY')
        api_secret = current_app.config.get('INSTAGRAM_API_SECRET')
        
        if not api_key or not api_secret:
            logger.error("Instagram API credentials not configured")
            return
        
        # Initialize Instagram client
        instagram_client = InstagramClient(api_key, api_secret)
        
        # Get all Instagram accounts from database
        instagram_accounts = SocialAccount.query.filter_by(platform='instagram').all()
        
        for account in instagram_accounts:
            try:
                # Fetch account metrics
                metrics = instagram_client.get_account_metrics(account.account_id)
                
                # Create new SocialMetric record
                social_metric = SocialMetric(
                    social_account_id=account.id,
                    timestamp=datetime.utcnow(),
                    followers=metrics.get('followers_count', 0),
                    likes=metrics.get('total_likes', 0),
                    comments=metrics.get('total_comments', 0),
                    shares=metrics.get('total_shares', 0),
                    views=metrics.get('total_views', 0)
                )
                
                # Store platform-specific data
                social_metric.set_platform_data({
                    'reach': metrics.get('reach', 0),
                    'impressions': metrics.get('impressions', 0),
                    'profile_views': metrics.get('profile_views', 0),
                    'engagement_rate': metrics.get('engagement_rate', 0)
                })
                
                db.session.add(social_metric)
                
                # Fetch recent posts
                posts = instagram_client.get_recent_posts(account.account_id)
                
                for post in posts:
                    # Check if content already exists
                    existing_content = Content.query.filter_by(
                        social_account_id=account.id,
                        content_id=post.get('id')
                    ).first()
                    
                    if existing_content:
                        # Update existing content
                        existing_content.likes = post.get('likes_count', 0)
                        existing_content.comments = post.get('comments_count', 0)
                        existing_content.shares = post.get('shares_count', 0)
                        existing_content.views = post.get('views_count', 0)
                    else:
                        # Create new content
                        content = Content(
                            social_account_id=account.id,
                            content_id=post.get('id'),
                            content_type=post.get('type', 'post'),
                            title=post.get('caption', '')[:200] if post.get('caption') else '',
                            description=post.get('caption'),
                            url=post.get('permalink'),
                            thumbnail_url=post.get('media_url'),
                            published_at=datetime.fromisoformat(post.get('timestamp')),
                            likes=post.get('likes_count', 0),
                            comments=post.get('comments_count', 0),
                            shares=post.get('shares_count', 0),
                            views=post.get('views_count', 0)
                        )
                        
                        # Store additional metadata
                        content.set_content_metadata({
                            'media_type': post.get('media_type'),
                            'hashtags': post.get('hashtags', []),
                            'mentions': post.get('mentions', []),
                            'location': post.get('location')
                        })
                        
                        db.session.add(content)
                
                db.session.commit()
                logger.info(f"Successfully fetched Instagram data for account {account.account_name}")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error fetching Instagram data for account {account.account_name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in Instagram data fetch process: {str(e)}")

def fetch_youtube_data():
    """Fetch data from YouTube for all registered business channels."""
    logger.info("Starting YouTube data fetch")
    
    try:
        # Get YouTube API key from config
        api_key = current_app.config.get('YOUTUBE_API_KEY')
        
        if not api_key:
            logger.error("YouTube API key not configured")
            return
        
        # Initialize YouTube client
        youtube_client = YouTubeClient(api_key)
        
        # Get all YouTube accounts from database
        youtube_accounts = SocialAccount.query.filter_by(platform='youtube').all()
        
        for account in youtube_accounts:
            try:
                # Fetch channel metrics
                metrics = youtube_client.get_channel_metrics(account.account_id)
                
                # Create new SocialMetric record
                social_metric = SocialMetric(
                    social_account_id=account.id,
                    timestamp=datetime.utcnow(),
                    followers=metrics.get('subscriber_count', 0),
                    likes=metrics.get('total_likes', 0),
                    comments=metrics.get('total_comments', 0),
                    shares=metrics.get('total_shares', 0),
                    views=metrics.get('total_views', 0)
                )
                
                # Store platform-specific data
                social_metric.set_platform_data({
                    'watch_time': metrics.get('watch_time_hours', 0),
                    'average_view_duration': metrics.get('average_view_duration', 0),
                    'click_through_rate': metrics.get('click_through_rate', 0),
                    'unique_viewers': metrics.get('unique_viewers', 0)
                })
                
                db.session.add(social_metric)
                
                # Fetch recent videos
                videos = youtube_client.get_recent_videos(account.account_id)
                
                for video in videos:
                    # Check if content already exists
                    existing_content = Content.query.filter_by(
                        social_account_id=account.id,
                        content_id=video.get('id')
                    ).first()
                    
                    if existing_content:
                        # Update existing content
                        existing_content.likes = video.get('likes', 0)
                        existing_content.comments = video.get('comments', 0)
                        existing_content.shares = video.get('shares', 0)
                        existing_content.views = video.get('views', 0)
                    else:
                        # Create new content
                        content = Content(
                            social_account_id=account.id,
                            content_id=video.get('id'),
                            content_type='video',
                            title=video.get('title', '')[:200],
                            description=video.get('description'),
                            url=f"https://www.youtube.com/watch?v={video.get('id')}",
                            thumbnail_url=video.get('thumbnail_url'),
                            published_at=datetime.fromisoformat(video.get('published_at')),
                            likes=video.get('likes', 0),
                            comments=video.get('comments', 0),
                            shares=video.get('shares', 0),
                            views=video.get('views', 0)
                        )
                        
                        # Store additional metadata
                        content.set_content_metadata({
                            'duration': video.get('duration'),
                            'tags': video.get('tags', []),
                            'category_id': video.get('category_id'),
                            'definition': video.get('definition'),
                            'caption': video.get('caption')
                        })
                        
                        db.session.add(content)
                
                db.session.commit()
                logger.info(f"Successfully fetched YouTube data for channel {account.account_name}")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error fetching YouTube data for channel {account.account_name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in YouTube data fetch process: {str(e)}")

def fetch_tiktok_data():
    """Fetch data from TikTok for all registered business accounts."""
    logger.info("Starting TikTok data fetch")
    
    try:
        # Get TikTok API credentials from config
        api_key = current_app.config.get('TIKTOK_API_KEY')
        api_secret = current_app.config.get('TIKTOK_API_SECRET')
        
        if not api_key or not api_secret:
            logger.error("TikTok API credentials not configured")
            return
        
        # Initialize TikTok client
        tiktok_client = TikTokClient(api_key, api_secret)
        
        # Get all TikTok accounts from database
        tiktok_accounts = SocialAccount.query.filter_by(platform='tiktok').all()
        
        for account in tiktok_accounts:
            try:
                # Fetch account metrics
                metrics = tiktok_client.get_account_metrics(account.account_id)
                
                # Create new SocialMetric record
                social_metric = SocialMetric(
                    social_account_id=account.id,
                    timestamp=datetime.utcnow(),
                    followers=metrics.get('follower_count', 0),
                    likes=metrics.get('total_likes', 0),
                    comments=metrics.get('total_comments', 0),
                    shares=metrics.get('total_shares', 0),
                    views=metrics.get('total_views', 0)
                )
                
                # Store platform-specific data
                social_metric.set_platform_data({
                    'profile_views': metrics.get('profile_views', 0),
                    'video_views': metrics.get('video_views', 0),
                    'engagement_rate': metrics.get('engagement_rate', 0),
                    'average_watch_time': metrics.get('average_watch_time', 0)
                })
                
                db.session.add(social_metric)
                
                # Fetch recent videos
                videos = tiktok_client.get_recent_videos(account.account_id)
                
                for video in videos:
                    # Check if content already exists
                    existing_content = Content.query.filter_by(
                        social_account_id=account.id,
                        content_id=video.get('id')
                    ).first()
                    
                    if existing_content:
                        # Update existing content
                        existing_content.likes = video.get('likes', 0)
                        existing_content.comments = video.get('comments', 0)
                        existing_content.shares = video.get('shares', 0)
                        existing_content.views = video.get('views', 0)
                    else:
                        # Create new content
                        content = Content(
                            social_account_id=account.id,
                            content_id=video.get('id'),
                            content_type='video',
                            title=video.get('description', '')[:200] if video.get('description') else '',
                            description=video.get('description'),
                            url=video.get('share_url'),
                            thumbnail_url=video.get('cover_image_url'),
                            published_at=datetime.fromisoformat(video.get('create_time')),
                            likes=video.get('likes', 0),
                            comments=video.get('comments', 0),
                            shares=video.get('shares', 0),
                            views=video.get('views', 0)
                        )
                        
                        # Store additional metadata
                        content.set_content_metadata({
                            'duration': video.get('duration'),
                            'hashtags': video.get('hashtags', []),
                            'music': video.get('music'),
                            'video_format': video.get('format'),
                            'region': video.get('region')
                        })
                        
                        db.session.add(content)
                
                db.session.commit()
                logger.info(f"Successfully fetched TikTok data for account {account.account_name}")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error fetching TikTok data for account {account.account_name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in TikTok data fetch process: {str(e)}")
