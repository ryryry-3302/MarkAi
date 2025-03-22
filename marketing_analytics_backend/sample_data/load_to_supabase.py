#!/usr/bin/env python3
"""
Script to load video and metadata files into Supabase.
This script processes files from the data directory and stores them in Supabase.
"""
import os
import json
import logging
import argparse
from pathlib import Path
from database.supabase_client import get_supabase_client
from sample_data.instagram_processor import process_instagram_content
from sample_data.processor import process_video_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_metadata_files(metadata_dir):
    """
    Load metadata files from the specified directory.
    
    Args:
        metadata_dir: Path to the directory containing metadata files
        
    Returns:
        List of processed content items
    """
    metadata_path = Path(metadata_dir)
    if not metadata_path.exists():
        logger.error(f"Metadata directory not found: {metadata_dir}")
        return []
    
    processed_items = []
    
    for file_path in metadata_path.glob('*.json'):
        logger.info(f"Processing metadata file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content_data = json.load(f)
                
                # Handle both single item and array formats
                if isinstance(content_data, list):
                    for item in content_data:
                        processed_content = process_instagram_content(item)
                        if processed_content:
                            processed_items.append(processed_content)
                else:
                    processed_content = process_instagram_content(content_data)
                    if processed_content:
                        processed_items.append(processed_content)
                        
        except Exception as e:
            logger.error(f"Error processing metadata file {file_path}: {str(e)}")
    
    return processed_items

def load_video_files(videos_dir):
    """
    Load video files from the specified directory.
    
    Args:
        videos_dir: Path to the directory containing video files
        
    Returns:
        List of processed video items
    """
    videos_path = Path(videos_dir)
    if not videos_path.exists():
        logger.error(f"Videos directory not found: {videos_dir}")
        return []
    
    processed_items = []
    
    for file_path in videos_path.glob('*.mp4'):
        logger.info(f"Processing video file: {file_path}")
        try:
            processed_video = process_video_content(str(file_path))
            if processed_video:
                processed_items.append(processed_video)
        except Exception as e:
            logger.error(f"Error processing video file {file_path}: {str(e)}")
    
    return processed_items

def store_in_supabase(items):
    """
    Store processed items in Supabase.
    
    Args:
        items: List of processed content items
        
    Returns:
        Number of items successfully stored
    """
    if not items:
        logger.info("No items to store")
        return 0
    
    supabase = get_supabase_client()
    stored_count = 0
    
    for item in items:
        try:
            stored_item = supabase.store_content(item)
            if stored_item:
                stored_count += 1
                logger.info(f"Stored item: {item.get('id', item.get('shortCode', 'unknown'))}")
        except Exception as e:
            logger.error(f"Error storing item in Supabase: {str(e)}")
    
    return stored_count

def main():
    """Main function to load data into Supabase."""
    parser = argparse.ArgumentParser(description='Load data into Supabase')
    parser.add_argument('--metadata-dir', default='data/metadata', help='Directory containing metadata files')
    parser.add_argument('--videos-dir', default='data/videos', help='Directory containing video files')
    parser.add_argument('--content-type', choices=['all', 'metadata', 'videos'], default='all', 
                        help='Type of content to process')
    
    args = parser.parse_args()
    
    processed_items = []
    
    # Process metadata files
    if args.content_type in ['all', 'metadata']:
        metadata_items = load_metadata_files(args.metadata_dir)
        processed_items.extend(metadata_items)
        logger.info(f"Processed {len(metadata_items)} metadata files")
    
    # Process video files
    if args.content_type in ['all', 'videos']:
        video_items = load_video_files(args.videos_dir)
        processed_items.extend(video_items)
        logger.info(f"Processed {len(video_items)} video files")
    
    # Store in Supabase
    stored_count = store_in_supabase(processed_items)
    logger.info(f"Successfully stored {stored_count} items in Supabase")

if __name__ == "__main__":
    main()
