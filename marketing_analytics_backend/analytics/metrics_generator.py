"""
Instagram Content Metrics Generator

This module analyzes Instagram content metadata to generate useful metrics and insights
for marketing analytics purposes.
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from collections import Counter
import re

class InstagramMetricsGenerator:
    """
    Generates metrics and insights from Instagram content metadata.
    """
    
    def __init__(self, metadata_dir: str, videos_dir: str):
        """
        Initialize the metrics generator.
        
        Args:
            metadata_dir: Directory containing JSON metadata files
            videos_dir: Directory containing video files
        """
        self.metadata_dir = metadata_dir
        self.videos_dir = videos_dir
        self.content_data = []
        self.load_content_data()
    
    def load_content_data(self) -> None:
        """Load all content data from JSON files in the metadata directory."""
        json_files = glob.glob(os.path.join(self.metadata_dir, "*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.content_data.extend(data)
                    else:
                        self.content_data.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """
        Calculate engagement metrics across all content.
        
        Returns:
            Dictionary containing engagement metrics
        """
        if not self.content_data:
            return {"error": "No content data available"}
        
        total_likes = sum(item.get('likesCount', 0) for item in self.content_data)
        total_comments = sum(item.get('commentsCount', 0) for item in self.content_data)
        total_views = sum(item.get('videoViewCount', 0) for item in self.content_data if item.get('type') == 'Video')
        total_plays = sum(item.get('videoPlayCount', 0) for item in self.content_data if item.get('type') == 'Video')
        
        # Calculate engagement rate (likes + comments / total content)
        content_count = len(self.content_data)
        avg_likes = total_likes / content_count if content_count > 0 else 0
        avg_comments = total_comments / content_count if content_count > 0 else 0
        
        # Video specific metrics
        video_count = sum(1 for item in self.content_data if item.get('type') == 'Video')
        avg_views = total_views / video_count if video_count > 0 else 0
        avg_plays = total_plays / video_count if video_count > 0 else 0
        
        # Calculate completion rate for videos (views / plays)
        completion_rate = total_views / total_plays if total_plays > 0 else 0
        
        return {
            "total_content": content_count,
            "total_videos": video_count,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_views": total_views,
            "total_plays": total_plays,
            "avg_likes_per_content": avg_likes,
            "avg_comments_per_content": avg_comments,
            "avg_views_per_video": avg_views,
            "avg_plays_per_video": avg_plays,
            "video_completion_rate": completion_rate,
            "engagement_rate": (total_likes + total_comments) / content_count if content_count > 0 else 0
        }
    
    def get_content_performance(self) -> List[Dict[str, Any]]:
        """
        Analyze performance of individual content items.
        
        Returns:
            List of content items with performance metrics
        """
        if not self.content_data:
            return [{"error": "No content data available"}]
        
        performance_data = []
        
        for item in self.content_data:
            engagement = item.get('likesCount', 0) + item.get('commentsCount', 0)
            
            # For videos, include view metrics
            if item.get('type') == 'Video':
                views = item.get('videoViewCount', 0)
                plays = item.get('videoPlayCount', 0)
                completion_rate = views / plays if plays > 0 else 0
                
                performance_data.append({
                    "id": item.get('id'),
                    "shortCode": item.get('shortCode'),
                    "type": item.get('type'),
                    "caption": item.get('caption'),
                    "url": item.get('url'),
                    "timestamp": item.get('timestamp'),
                    "likes": item.get('likesCount', 0),
                    "comments": item.get('commentsCount', 0),
                    "views": views,
                    "plays": plays,
                    "completion_rate": completion_rate,
                    "total_engagement": engagement,
                    "duration": item.get('videoDuration', 0)
                })
            else:
                # For non-video content
                performance_data.append({
                    "id": item.get('id'),
                    "shortCode": item.get('shortCode'),
                    "type": item.get('type'),
                    "caption": item.get('caption'),
                    "url": item.get('url'),
                    "timestamp": item.get('timestamp'),
                    "likes": item.get('likesCount', 0),
                    "comments": item.get('commentsCount', 0),
                    "total_engagement": engagement
                })
        
        # Sort by total engagement (descending)
        performance_data.sort(key=lambda x: x.get('total_engagement', 0), reverse=True)
        
        return performance_data
    
    def get_hashtag_analysis(self) -> Dict[str, Any]:
        """
        Analyze hashtag usage and performance.
        
        Returns:
            Dictionary containing hashtag metrics
        """
        if not self.content_data:
            return {"error": "No content data available"}
        
        # Extract all hashtags
        all_hashtags = []
        hashtag_performance = {}
        
        for item in self.content_data:
            hashtags = item.get('hashtags', [])
            engagement = item.get('likesCount', 0) + item.get('commentsCount', 0)
            
            all_hashtags.extend(hashtags)
            
            # Track performance per hashtag
            for tag in hashtags:
                if tag not in hashtag_performance:
                    hashtag_performance[tag] = {
                        "count": 0,
                        "total_engagement": 0,
                        "content_ids": []
                    }
                
                hashtag_performance[tag]["count"] += 1
                hashtag_performance[tag]["total_engagement"] += engagement
                hashtag_performance[tag]["content_ids"].append(item.get('id'))
        
        # Calculate frequency
        hashtag_frequency = dict(Counter(all_hashtags))
        
        # Calculate average engagement per hashtag
        for tag, data in hashtag_performance.items():
            data["avg_engagement"] = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
        
        # Sort hashtags by frequency
        top_hashtags = sorted(hashtag_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Sort hashtags by engagement
        top_engaging_hashtags = sorted(
            hashtag_performance.items(), 
            key=lambda x: x[1]["avg_engagement"], 
            reverse=True
        )
        
        return {
            "total_hashtags_used": len(all_hashtags),
            "unique_hashtags": len(hashtag_frequency),
            "top_hashtags": top_hashtags[:10],
            "top_engaging_hashtags": [(tag, data["avg_engagement"]) for tag, data in top_engaging_hashtags[:10]],
            "hashtag_details": hashtag_performance
        }
    
    def get_mention_analysis(self) -> Dict[str, Any]:
        """
        Analyze mentions and their performance.
        
        Returns:
            Dictionary containing mention metrics
        """
        if not self.content_data:
            return {"error": "No content data available"}
        
        # Extract all mentions
        all_mentions = []
        mention_performance = {}
        
        for item in self.content_data:
            mentions = item.get('mentions', [])
            engagement = item.get('likesCount', 0) + item.get('commentsCount', 0)
            
            all_mentions.extend(mentions)
            
            # Track performance per mention
            for mention in mentions:
                if mention not in mention_performance:
                    mention_performance[mention] = {
                        "count": 0,
                        "total_engagement": 0,
                        "content_ids": []
                    }
                
                mention_performance[mention]["count"] += 1
                mention_performance[mention]["total_engagement"] += engagement
                mention_performance[mention]["content_ids"].append(item.get('id'))
        
        # Calculate frequency
        mention_frequency = dict(Counter(all_mentions))
        
        # Calculate average engagement per mention
        for mention, data in mention_performance.items():
            data["avg_engagement"] = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
        
        # Sort mentions by frequency
        top_mentions = sorted(mention_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Sort mentions by engagement
        top_engaging_mentions = sorted(
            mention_performance.items(), 
            key=lambda x: x[1]["avg_engagement"], 
            reverse=True
        )
        
        return {
            "total_mentions": len(all_mentions),
            "unique_mentions": len(mention_frequency),
            "top_mentions": top_mentions[:10],
            "top_engaging_mentions": [(mention, data["avg_engagement"]) for mention, data in top_engaging_mentions[:10]],
            "mention_details": mention_performance
        }
    
    def get_posting_time_analysis(self) -> Dict[str, Any]:
        """
        Analyze posting times and their impact on engagement.
        
        Returns:
            Dictionary containing posting time metrics
        """
        if not self.content_data:
            return {"error": "No content data available"}
        
        # Parse timestamps and extract hour data
        hour_engagement = {}
        weekday_engagement = {}
        
        for item in self.content_data:
            timestamp_str = item.get('timestamp')
            if not timestamp_str:
                continue
                
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                hour = timestamp.hour
                weekday = timestamp.weekday()  # 0 = Monday, 6 = Sunday
                
                engagement = item.get('likesCount', 0) + item.get('commentsCount', 0)
                
                # Track by hour
                if hour not in hour_engagement:
                    hour_engagement[hour] = {
                        "count": 0,
                        "total_engagement": 0
                    }
                
                hour_engagement[hour]["count"] += 1
                hour_engagement[hour]["total_engagement"] += engagement
                
                # Track by weekday
                if weekday not in weekday_engagement:
                    weekday_engagement[weekday] = {
                        "count": 0,
                        "total_engagement": 0
                    }
                
                weekday_engagement[weekday]["count"] += 1
                weekday_engagement[weekday]["total_engagement"] += engagement
                
            except Exception as e:
                print(f"Error parsing timestamp {timestamp_str}: {e}")
        
        # Calculate average engagement per hour and weekday
        for hour, data in hour_engagement.items():
            data["avg_engagement"] = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
        
        for weekday, data in weekday_engagement.items():
            data["avg_engagement"] = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
        
        # Find best posting times
        best_hours = sorted(
            hour_engagement.items(), 
            key=lambda x: x[1]["avg_engagement"], 
            reverse=True
        )
        
        best_weekdays = sorted(
            weekday_engagement.items(), 
            key=lambda x: x[1]["avg_engagement"], 
            reverse=True
        )
        
        # Convert weekday numbers to names
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        best_weekdays_named = [(weekday_names[day], data["avg_engagement"]) for day, data in best_weekdays]
        
        return {
            "best_posting_hours": [(hour, data["avg_engagement"]) for hour, data in best_hours],
            "best_posting_weekdays": best_weekdays_named,
            "hour_details": hour_engagement,
            "weekday_details": {weekday_names[day]: data for day, data in weekday_engagement.items()}
        }
    
    def get_content_insights(self) -> Dict[str, Any]:
        """
        Generate insights about the content.
        
        Returns:
            Dictionary containing content insights
        """
        if not self.content_data:
            return {"error": "No content data available"}
        
        # Analyze caption length vs. engagement
        caption_analysis = []
        
        for item in self.content_data:
            caption = item.get('caption', '')
            caption_length = len(caption) if caption else 0
            engagement = item.get('likesCount', 0) + item.get('commentsCount', 0)
            
            caption_analysis.append({
                "id": item.get('id'),
                "caption_length": caption_length,
                "engagement": engagement
            })
        
        # Group by caption length ranges
        length_ranges = {
            "short (0-50)": {"count": 0, "total_engagement": 0},
            "medium (51-150)": {"count": 0, "total_engagement": 0},
            "long (151+)": {"count": 0, "total_engagement": 0}
        }
        
        for item in caption_analysis:
            length = item["caption_length"]
            engagement = item["engagement"]
            
            if length <= 50:
                length_ranges["short (0-50)"]["count"] += 1
                length_ranges["short (0-50)"]["total_engagement"] += engagement
            elif length <= 150:
                length_ranges["medium (51-150)"]["count"] += 1
                length_ranges["medium (51-150)"]["total_engagement"] += engagement
            else:
                length_ranges["long (151+)"]["count"] += 1
                length_ranges["long (151+)"]["total_engagement"] += engagement
        
        # Calculate average engagement per length range
        for range_name, data in length_ranges.items():
            data["avg_engagement"] = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
        
        # Analyze video duration vs. engagement (for videos only)
        duration_analysis = []
        
        for item in self.content_data:
            if item.get('type') != 'Video':
                continue
                
            duration = item.get('videoDuration', 0)
            engagement = item.get('likesCount', 0) + item.get('commentsCount', 0)
            views = item.get('videoViewCount', 0)
            
            duration_analysis.append({
                "id": item.get('id'),
                "duration": duration,
                "engagement": engagement,
                "views": views
            })
        
        # Group by duration ranges
        duration_ranges = {
            "short (0-30s)": {"count": 0, "total_engagement": 0, "total_views": 0},
            "medium (31-60s)": {"count": 0, "total_engagement": 0, "total_views": 0},
            "long (61s+)": {"count": 0, "total_engagement": 0, "total_views": 0}
        }
        
        for item in duration_analysis:
            duration = item["duration"]
            engagement = item["engagement"]
            views = item["views"]
            
            if duration <= 30:
                duration_ranges["short (0-30s)"]["count"] += 1
                duration_ranges["short (0-30s)"]["total_engagement"] += engagement
                duration_ranges["short (0-30s)"]["total_views"] += views
            elif duration <= 60:
                duration_ranges["medium (31-60s)"]["count"] += 1
                duration_ranges["medium (31-60s)"]["total_engagement"] += engagement
                duration_ranges["medium (31-60s)"]["total_views"] += views
            else:
                duration_ranges["long (61s+)"]["count"] += 1
                duration_ranges["long (61s+)"]["total_engagement"] += engagement
                duration_ranges["long (61s+)"]["total_views"] += views
        
        # Calculate average engagement and views per duration range
        for range_name, data in duration_ranges.items():
            data["avg_engagement"] = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
            data["avg_views"] = data["total_views"] / data["count"] if data["count"] > 0 else 0
        
        return {
            "caption_length_analysis": {
                "ranges": length_ranges,
                "best_performing_length": max(length_ranges.items(), key=lambda x: x[1]["avg_engagement"])[0]
            },
            "video_duration_analysis": {
                "ranges": duration_ranges,
                "best_performing_duration": max(duration_ranges.items(), key=lambda x: x[1]["avg_engagement"])[0]
            }
        }
    
    def get_sentiment_analysis(self) -> Dict[str, Any]:
        """
        Basic sentiment analysis of comments.
        
        Returns:
            Dictionary containing sentiment metrics
        """
        # This is a simple implementation - for production, use a proper NLP library
        positive_words = [
            'good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'beautiful', 
            'perfect', 'best', 'fantastic', 'wonderful', 'happy', 'nice', 'brilliant',
            'outstanding', 'superb', 'impressive', 'exceptional', 'terrific', 'fabulous'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'disappointing', 'worst',
            'hate', 'dislike', 'mediocre', 'useless', 'boring', 'stupid', 'waste',
            'annoying', 'frustrating', 'pathetic', 'ridiculous', 'lousy', 'unpleasant'
        ]
        
        sentiment_data = {
            "total_comments_analyzed": 0,
            "positive_comments": 0,
            "negative_comments": 0,
            "neutral_comments": 0,
            "content_sentiment": {}
        }
        
        for item in self.content_data:
            content_id = item.get('id')
            comments = item.get('latestComments', [])
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for comment in comments:
                text = comment.get('text', '').lower()
                if not text:
                    continue
                
                sentiment_data["total_comments_analyzed"] += 1
                
                # Count positive and negative words
                pos_count = sum(1 for word in positive_words if word in text)
                neg_count = sum(1 for word in negative_words if word in text)
                
                # Determine sentiment
                if pos_count > neg_count:
                    positive_count += 1
                    sentiment_data["positive_comments"] += 1
                elif neg_count > pos_count:
                    negative_count += 1
                    sentiment_data["negative_comments"] += 1
                else:
                    neutral_count += 1
                    sentiment_data["neutral_comments"] += 1
            
            # Store sentiment for this content
            sentiment_data["content_sentiment"][content_id] = {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "total": positive_count + negative_count + neutral_count
            }
        
        # Calculate percentages
        total = sentiment_data["total_comments_analyzed"]
        if total > 0:
            sentiment_data["positive_percentage"] = (sentiment_data["positive_comments"] / total) * 100
            sentiment_data["negative_percentage"] = (sentiment_data["negative_comments"] / total) * 100
            sentiment_data["neutral_percentage"] = (sentiment_data["neutral_comments"] / total) * 100
        
        return sentiment_data
    
    def generate_all_metrics(self) -> Dict[str, Any]:
        """
        Generate all available metrics and insights.
        
        Returns:
            Dictionary containing all metrics
        """
        return {
            "engagement_metrics": self.get_engagement_metrics(),
            "content_performance": self.get_content_performance(),
            "hashtag_analysis": self.get_hashtag_analysis(),
            "mention_analysis": self.get_mention_analysis(),
            "posting_time_analysis": self.get_posting_time_analysis(),
            "content_insights": self.get_content_insights(),
            "sentiment_analysis": self.get_sentiment_analysis()
        }


if __name__ == "__main__":
    # Example usage
    metadata_dir = "../data/metadata"
    videos_dir = "../data/videos"
    
    metrics_generator = InstagramMetricsGenerator(metadata_dir, videos_dir)
    metrics = metrics_generator.generate_all_metrics()
    
    print(json.dumps(metrics, indent=2))
