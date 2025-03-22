"""
Instagram content processor for the new metadata format.
Processes Instagram content data from the new JSON format.
"""
import json
import logging
from datetime import datetime
from database.supabase_client import SupabaseClient
from gemini_integration.client import GeminiClient

logger = logging.getLogger(__name__)

def process_instagram_content(content_data):
    """
    Process Instagram content data in the new format and store in database.
    
    Args:
        content_data: Dictionary containing Instagram content data in the new format
    
    Returns:
        Dictionary containing the processed content
    """
    try:
        # The content_data is already in the format we need for Supabase storage
        # Just ensure all required fields are present
        
        # Add platform field if not present
        if 'platform' not in content_data:
            content_data['platform'] = 'instagram'
            
        # Add timestamp if not present
        if 'timestamp' not in content_data:
            content_data['timestamp'] = datetime.now().isoformat()
            
        # Add default values for missing fields
        if 'likesCount' not in content_data:
            content_data['likesCount'] = 0
            
        if 'commentsCount' not in content_data:
            content_data['commentsCount'] = 0
            
        if 'videoViewCount' not in content_data:
            content_data['videoViewCount'] = 0
            
        # Make sure we have an ID
        if 'id' not in content_data and 'shortCode' in content_data:
            content_data['id'] = content_data['shortCode']
        elif 'id' not in content_data:
            content_data['id'] = f"instagram_{datetime.now().timestamp()}"
            
        logger.info(f"Processed Instagram content: {content_data.get('id')}")
        # Generate insights if Gemini API key is available
        try:
            import os
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if gemini_api_key:
                generate_instagram_insights(content_data, gemini_api_key)
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            
        return content_data
    except Exception as e:
        logger.error(f"Error processing Instagram content: {str(e)}")
        return None

def process_video_content(video_path):
    """
    Process a video file and store metadata in database.
    
    Args:
        video_path: Path to the video file
    
    Returns:
        Dictionary containing the processed video metadata
    """
    try:
        # Get basic file information
        import os
        from pathlib import Path
        
        file_path = Path(video_path)
        filename = file_path.name
        file_size = file_path.stat().st_size
        content_id = f"video_{file_path.stem}"
        
        # Try to extract some metadata from the filename
        # For example, if the filename contains a caption
        title = filename
        description = f"Video file: {filename}"
        
        # If the filename is long, it might contain a description
        if len(filename) > 30 and '.' in filename:
            parts = filename.split('.')
            if len(parts) > 1:
                potential_description = parts[0]
                if len(potential_description) > 20:
                    title = potential_description[:50]
                    description = potential_description
        
        # Basic metadata
        metadata = {
            'filename': filename,
            'fileSize': file_size,
            'fileExtension': file_path.suffix,
            'duration': 0,  # Would require video processing library
            'resolution': '1920x1080',  # Placeholder
            'format': 'mp4',
            'platform': 'instagram',  # Assuming Instagram as default platform
            'type': 'Video'
        }
        
        # Prepare content data for database
        content_entry = {
            'id': content_id,
            'type': 'Video',
            'title': title,
            'caption': description,
            'url': str(video_path),
            'displayUrl': str(video_path),  # Using file path as thumbnail URL
            'timestamp': datetime.now().isoformat(),
            'likesCount': 0,
            'commentsCount': 0,
            'videoViewCount': 0,
            'ownerUsername': 'local_user',
            'ownerFullName': 'Local User',
            'platform': 'instagram',
            # Add all metadata
            **metadata
        }
        
        logger.info(f"Processed video content: {content_id}")
        return content_entry
    except Exception as e:
        logger.error(f"Error processing video content: {str(e)}")
        return None

def generate_instagram_insights(content_entry, gemini_api_key):
    """
    Generate insights for Instagram content using Google Gemini.
    
    Args:
        content_entry: Content entry dictionary
        gemini_api_key: Google Gemini API key
    
    Returns:
        List of generated insights
    """
    try:
        # Initialize Gemini client
        gemini_client = GeminiClient(gemini_api_key)
        supabase = SupabaseClient()
        
        content_id = content_entry.get('content_id')
        metadata_str = content_entry.get('content_metadata')
        
        if not metadata_str:
            return []
        
        # Parse metadata
        try:
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError:
            return []
        
        # Extract fields from the new Instagram format
        hashtags = metadata.get('hashtags', [])
        mentions = metadata.get('mentions', [])
        comments_count = metadata.get('commentsCount', 0)
        latest_comments = metadata.get('latestComments', [])
        
        insights = []
        
        # Generate hashtag insights
        if hashtags:
            hashtag_prompt = f"Analyze these hashtags from an Instagram post: {', '.join(hashtags)}\n"
            hashtag_prompt += "Provide a brief analysis of what audience these hashtags target and their potential effectiveness."
            
            try:
                hashtag_analysis = gemini_client.generate_text(hashtag_prompt)
                
                hashtag_insight = {
                    'insight_type': 'hashtags',
                    'title': f"Hashtag Analysis for Instagram Content",
                    'content': hashtag_analysis
                }
                
                # Save to Supabase
                supabase.create_insight(
                    business_id=1,  # Default business ID
                    insight_type='hashtags',
                    title=hashtag_insight['title'],
                    content=hashtag_insight['content']
                )
                
                insights.append(hashtag_insight)
            except Exception as e:
                logger.error(f"Error generating hashtag analysis: {str(e)}")
        
        # Generate comment sentiment analysis
        if latest_comments:
            comment_prompt = f"Analyze the sentiment of these comments on an Instagram post:\n"
            for comment in latest_comments[:5]:  # Limit to 5 comments
                comment_prompt += f"- {comment.get('text', '')}\n"
            comment_prompt += "\nProvide a brief sentiment analysis summary."
            
            try:
                sentiment_analysis = gemini_client.generate_text(comment_prompt)
                
                comment_insight = {
                    'insight_type': 'comment_sentiment',
                    'title': f"Comment Sentiment Analysis for Instagram Content",
                    'content': sentiment_analysis
                }
                
                # Save to Supabase
                supabase.create_insight(
                    business_id=1,  # Default business ID
                    insight_type='comment_sentiment',
                    title=comment_insight['title'],
                    content=comment_insight['content']
                )
                
                insights.append(comment_insight)
            except Exception as e:
                logger.error(f"Error generating comment sentiment analysis: {str(e)}")
        
        return insights
    except Exception as e:
        logger.error(f"Error generating Instagram insights: {str(e)}")
        return []
