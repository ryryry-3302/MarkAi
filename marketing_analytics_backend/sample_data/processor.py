"""
Sample data processor for marketing analytics.
Loads sample JSON data and processes video content for analysis with Google Gemini.
"""
import json
import os
import logging
from datetime import datetime
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

def load_sample_data(data_dir, load_to_db=True):
    """
    Load sample data from JSON files and optionally store in database.
    
    Args:
        data_dir: Directory containing sample JSON files
        load_to_db: Whether to load the data into the database
        
    Returns:
        Dictionary containing the loaded data
    """
    data = {}
    
    # Load businesses
    with open(os.path.join(data_dir, "businesses.json"), "r") as f:
        data["businesses"] = json.load(f)
    
    # Load social accounts
    with open(os.path.join(data_dir, "social_accounts.json"), "r") as f:
        data["social_accounts"] = json.load(f)
    
    # Load metrics
    with open(os.path.join(data_dir, "metrics.json"), "r") as f:
        data["metrics"] = json.load(f)
    
    # Load content
    with open(os.path.join(data_dir, "content.json"), "r") as f:
        data["content"] = json.load(f)
        
    # Load Instagram-specific content if available
    instagram_content_path = os.path.join(data_dir, "instagram_content.json")
    if os.path.exists(instagram_content_path):
        with open(instagram_content_path, "r") as f:
            data["instagram_content"] = json.load(f)
    
    if load_to_db:
        load_data_to_database(data)
    
    return data

def process_instagram_content(content_data):
    """
    Process Instagram content data in the new format and store in database.
    
    Args:
        content_data: Dictionary containing Instagram content data in the new format
    
    Returns:
        Dictionary containing the processed content
    """
    try:
        # Initialize Supabase client
        supabase = SupabaseClient()
        
        # Extract data from the new format
        content_id = content_data.get('id')
        content_type = content_data.get('type', 'video')
        input_url = content_data.get('inputUrl', '')
        short_code = content_data.get('shortCode', '')
        caption = content_data.get('caption', '')
        hashtags = content_data.get('hashtags', [])
        mentions = content_data.get('mentions', [])
        comments_count = content_data.get('commentsCount', 0)
        latest_comments = content_data.get('latestComments', [])
        
        # Prepare content data for database
        content_entry = {
            'content_id': content_id,
            'content_type': content_type,
            'url': input_url,
            'title': caption[:100] if caption else '',  # Use first 100 chars of caption as title
            'description': caption,
            'published_at': datetime.now().isoformat(),
            'content_metadata': json.dumps({
                'shortCode': short_code,
                'hashtags': hashtags,
                'mentions': mentions,
                'commentsCount': comments_count,
                'latestComments': latest_comments
            })
        }
        
        # Insert into Supabase
        result = supabase.insert('content', content_entry)
        logger.info(f"Processed Instagram content: {content_id}")
        
        return content_entry
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
        # Initialize Supabase client
        supabase = SupabaseClient()
        
        # Get video metadata
        metadata = get_video_metadata(video_path)
        
        # Generate a content ID based on the filename
        filename = os.path.basename(video_path)
        content_id = f"video_{os.path.splitext(filename)[0]}"
        
        # Prepare content data for database
        content_entry = {
            'content_id': content_id,
            'content_type': 'video',
            'url': video_path,
            'title': metadata.get('title', filename),
            'description': metadata.get('description', ''),
            'published_at': datetime.now().isoformat(),
            'content_metadata': json.dumps(metadata)
        }
        
        # Insert into Supabase
        result = supabase.insert('content', content_entry)
        logger.info(f"Processed video content: {content_id}")
        
        return content_entry
    except Exception as e:
        logger.error(f"Error processing video content: {str(e)}")
        return None

def load_data_to_database(data):
    """
    Load sample data into the Supabase database.
    
    Args:
        data: Dictionary containing the sample data
    """
    try:
        # Initialize Supabase client
        supabase = SupabaseClient()
        
        # Use the bulk insert method to load all data
        success = supabase.load_sample_data(data)
        
        if success:
            logger.info("Successfully loaded sample data into Supabase database")
        else:
            logger.error("Failed to load sample data into Supabase database")
        
    except Exception as e:
        logger.error(f"Error loading sample data into database: {str(e)}")
        raise

def get_video_metadata(video_path):
    """
    Extract metadata from a video file.
    This is a placeholder function - in a real implementation, you would use
    a library like OpenCV or FFmpeg to extract actual metadata.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary containing video metadata
    """
    # In a real implementation, you would extract actual metadata from the video
    # For this example, we'll return placeholder data
    return {
        "duration": 30,  # seconds
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "format": "mp4",
        "has_audio": True
    }

def extract_video_frames(video_path, output_dir, num_frames=5):
    """
    Extract frames from a video file for analysis.
    This is a placeholder function - in a real implementation, you would use
    a library like OpenCV to extract actual frames.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        num_frames: Number of frames to extract
        
    Returns:
        List of paths to extracted frames
    """
    # In a real implementation, you would extract actual frames from the video
    # For this example, we'll return placeholder data
    os.makedirs(output_dir, exist_ok=True)
    
    frame_paths = []
    for i in range(num_frames):
        frame_path = os.path.join(output_dir, f"frame_{i}.jpg")
        # In a real implementation, you would save actual frames here
        frame_paths.append(frame_path)
    
    return frame_paths

def prepare_video_for_gemini(video_path, temp_dir):
    """
    Prepare a video for analysis with Google Gemini.
    Extracts metadata and frames from the video.
    
    Args:
        video_path: Path to the video file
        temp_dir: Directory to store temporary files
        
    Returns:
        Dictionary containing video data for Gemini
    """
    # Create a directory for the video frames
    video_id = os.path.basename(video_path).split('.')[0]
    frames_dir = os.path.join(temp_dir, video_id)
    
    # Extract metadata
    metadata = get_video_metadata(video_path)
    
    # Extract frames
    frame_paths = extract_video_frames(video_path, frames_dir)
    
    return {
        "video_path": video_path,
        "metadata": metadata,
        "frame_paths": frame_paths
    }

def process_sample_videos(sample_dir, temp_dir):
    """
    Process sample videos for analysis with Google Gemini.
    
    Args:
        sample_dir: Directory containing sample videos
        temp_dir: Directory to store temporary files
        
    Returns:
        Dictionary mapping content IDs to video data
    """
    video_data = {}
    
    # Get all video files in the sample directory
    video_files = [f for f in os.listdir(sample_dir) if f.endswith('.mp4')]
    
    for video_file in video_files:
        video_path = os.path.join(sample_dir, video_file)
        
        # Extract content ID from filename (assuming format: platform_type_id.mp4)
        content_id = int(video_file.split('_')[-1].split('.')[0])
        
        # Process the video
        video_data[content_id] = prepare_video_for_gemini(video_path, temp_dir)
    
    return video_data
