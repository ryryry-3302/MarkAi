"""
Instagram Content Insights Generator

This module generates human-readable insights and recommendations based on
the metrics generated from Instagram content metadata.
"""

import os
import json
from typing import Dict, List, Any, Optional
from metrics_generator import InstagramMetricsGenerator

class InstagramInsightsGenerator:
    """
    Generates human-readable insights and recommendations from Instagram metrics.
    """
    
    def __init__(self, metrics_data: Dict[str, Any] = None, metadata_dir: str = None, videos_dir: str = None):
        """
        Initialize the insights generator.
        
        Args:
            metrics_data: Pre-generated metrics data (optional)
            metadata_dir: Directory containing JSON metadata files (optional)
            videos_dir: Directory containing video files (optional)
        """
        if metrics_data:
            self.metrics = metrics_data
        elif metadata_dir and videos_dir:
            metrics_generator = InstagramMetricsGenerator(metadata_dir, videos_dir)
            self.metrics = metrics_generator.generate_all_metrics()
        else:
            raise ValueError("Either metrics_data or both metadata_dir and videos_dir must be provided")
    
    def generate_engagement_insights(self) -> List[str]:
        """
        Generate insights about engagement metrics.
        
        Returns:
            List of insight strings
        """
        insights = []
        engagement_metrics = self.metrics.get('engagement_metrics', {})
        
        if "error" in engagement_metrics:
            return ["No engagement data available to analyze."]
        
        # Overall engagement insights
        total_content = engagement_metrics.get('total_content', 0)
        total_likes = engagement_metrics.get('total_likes', 0)
        total_comments = engagement_metrics.get('total_comments', 0)
        engagement_rate = engagement_metrics.get('engagement_rate', 0)
        
        insights.append(f"Your content has generated a total of {total_likes:,} likes and {total_comments:,} comments across {total_content} posts.")
        
        if engagement_rate > 0.1:
            insights.append(f"Your overall engagement rate is {engagement_rate:.2%}, which is excellent compared to industry averages.")
        elif engagement_rate > 0.03:
            insights.append(f"Your overall engagement rate is {engagement_rate:.2%}, which is good compared to industry averages.")
        else:
            insights.append(f"Your overall engagement rate is {engagement_rate:.2%}, which is below average. Consider strategies to boost engagement.")
        
        # Video-specific insights
        if engagement_metrics.get('total_videos', 0) > 0:
            total_videos = engagement_metrics.get('total_videos', 0)
            total_views = engagement_metrics.get('total_views', 0)
            total_plays = engagement_metrics.get('total_plays', 0)
            completion_rate = engagement_metrics.get('video_completion_rate', 0)
            
            insights.append(f"Your {total_videos} videos have accumulated {total_views:,} views and {total_plays:,} plays.")
            
            if completion_rate > 0.7:
                insights.append(f"Your video completion rate is {completion_rate:.2%}, which is excellent. Viewers are highly engaged with your content.")
            elif completion_rate > 0.4:
                insights.append(f"Your video completion rate is {completion_rate:.2%}, which is average. Consider optimizing video length or content to improve viewer retention.")
            else:
                insights.append(f"Your video completion rate is {completion_rate:.2%}, which is below average. Focus on creating more engaging video content that captures attention early.")
        
        return insights
    
    def generate_content_performance_insights(self) -> List[str]:
        """
        Generate insights about content performance.
        
        Returns:
            List of insight strings
        """
        insights = []
        content_performance = self.metrics.get('content_performance', [])
        
        if not content_performance or "error" in content_performance[0]:
            return ["No content performance data available to analyze."]
        
        # Top performing content
        top_content = content_performance[:3] if len(content_performance) >= 3 else content_performance
        
        insights.append("Your top performing content:")
        for i, content in enumerate(top_content, 1):
            caption = content.get('caption', '')
            caption_preview = caption[:50] + "..." if len(caption) > 50 else caption
            engagement = content.get('total_engagement', 0)
            insights.append(f"{i}. {caption_preview} - {engagement:,} total engagement")
        
        # Content type performance
        video_content = [c for c in content_performance if c.get('type') == 'Video']
        image_content = [c for c in content_performance if c.get('type') != 'Video']
        
        if video_content and image_content:
            avg_video_engagement = sum(v.get('total_engagement', 0) for v in video_content) / len(video_content)
            avg_image_engagement = sum(i.get('total_engagement', 0) for i in image_content) / len(image_content)
            
            if avg_video_engagement > avg_image_engagement:
                insights.append(f"Videos perform better than other content types with {avg_video_engagement:.1f} vs {avg_image_engagement:.1f} average engagement.")
            else:
                insights.append(f"Images/carousels perform better than videos with {avg_image_engagement:.1f} vs {avg_video_engagement:.1f} average engagement.")
        
        # Underperforming content
        if len(content_performance) > 5:
            bottom_content = content_performance[-3:]
            avg_engagement = sum(c.get('total_engagement', 0) for c in content_performance) / len(content_performance)
            
            insights.append("Content that could be improved:")
            for content in bottom_content:
                caption = content.get('caption', '')
                caption_preview = caption[:50] + "..." if len(caption) > 50 else caption
                engagement = content.get('total_engagement', 0)
                
                if engagement < avg_engagement * 0.5:
                    insights.append(f"- {caption_preview} - Only {engagement:,} total engagement (less than 50% of your average)")
        
        return insights
    
    def generate_hashtag_insights(self) -> List[str]:
        """
        Generate insights about hashtag performance.
        
        Returns:
            List of insight strings
        """
        insights = []
        hashtag_analysis = self.metrics.get('hashtag_analysis', {})
        
        if "error" in hashtag_analysis:
            return ["No hashtag data available to analyze."]
        
        unique_hashtags = hashtag_analysis.get('unique_hashtags', 0)
        top_hashtags = hashtag_analysis.get('top_hashtags', [])
        top_engaging_hashtags = hashtag_analysis.get('top_engaging_hashtags', [])
        
        insights.append(f"You've used {unique_hashtags} unique hashtags across your content.")
        
        if top_hashtags:
            insights.append("Your most frequently used hashtags:")
            for i, (tag, count) in enumerate(top_hashtags[:5], 1):
                insights.append(f"{i}. #{tag} - used {count} times")
        
        if top_engaging_hashtags:
            insights.append("Hashtags with highest engagement:")
            for i, (tag, engagement) in enumerate(top_engaging_hashtags[:5], 1):
                insights.append(f"{i}. #{tag} - {engagement:.1f} average engagement")
        
        # Recommendations
        if top_engaging_hashtags and top_hashtags:
            # Find hashtags that are high-engaging but not frequently used
            top_tags = [tag for tag, _ in top_hashtags[:5]]
            recommended_tags = []
            
            for tag, engagement in top_engaging_hashtags:
                if tag not in top_tags and len(recommended_tags) < 3:
                    recommended_tags.append((tag, engagement))
            
            if recommended_tags:
                insights.append("Recommended hashtags to use more frequently based on engagement:")
                for i, (tag, engagement) in enumerate(recommended_tags, 1):
                    insights.append(f"{i}. #{tag} - {engagement:.1f} average engagement")
        
        return insights
    
    def generate_mention_insights(self) -> List[str]:
        """
        Generate insights about mention performance.
        
        Returns:
            List of insight strings
        """
        insights = []
        mention_analysis = self.metrics.get('mention_analysis', {})
        
        if "error" in mention_analysis:
            return ["No mention data available to analyze."]
        
        unique_mentions = mention_analysis.get('unique_mentions', 0)
        top_mentions = mention_analysis.get('top_mentions', [])
        top_engaging_mentions = mention_analysis.get('top_engaging_mentions', [])
        
        insights.append(f"You've mentioned {unique_mentions} unique accounts across your content.")
        
        if top_mentions:
            insights.append("Your most frequently mentioned accounts:")
            for i, (mention, count) in enumerate(top_mentions[:3], 1):
                insights.append(f"{i}. @{mention} - mentioned {count} times")
        
        if top_engaging_mentions:
            insights.append("Mentions with highest engagement:")
            for i, (mention, engagement) in enumerate(top_engaging_mentions[:3], 1):
                insights.append(f"{i}. @{mention} - {engagement:.1f} average engagement")
        
        # Recommendations
        if top_engaging_mentions and len(top_engaging_mentions) > 3:
            insights.append("Consider collaborating more with these high-engagement accounts:")
            for i, (mention, engagement) in enumerate(top_engaging_mentions[:3], 1):
                insights.append(f"{i}. @{mention} - content with this mention averages {engagement:.1f} engagement")
        
        return insights
    
    def generate_posting_time_insights(self) -> List[str]:
        """
        Generate insights about posting times.
        
        Returns:
            List of insight strings
        """
        insights = []
        posting_analysis = self.metrics.get('posting_time_analysis', {})
        
        if "error" in posting_analysis:
            return ["No posting time data available to analyze."]
        
        best_hours = posting_analysis.get('best_posting_hours', [])
        best_weekdays = posting_analysis.get('best_posting_weekdays', [])
        
        if best_hours:
            insights.append("Best times to post based on engagement:")
            for i, (hour, engagement) in enumerate(best_hours[:3], 1):
                am_pm = "AM" if hour < 12 else "PM"
                display_hour = hour if hour <= 12 else hour - 12
                display_hour = 12 if display_hour == 0 else display_hour
                insights.append(f"{i}. {display_hour} {am_pm} - {engagement:.1f} average engagement")
        
        if best_weekdays:
            insights.append("Best days to post based on engagement:")
            for i, (day, engagement) in enumerate(best_weekdays[:3], 1):
                insights.append(f"{i}. {day} - {engagement:.1f} average engagement")
        
        # Recommendations
        if best_hours and best_weekdays:
            top_day = best_weekdays[0][0] if best_weekdays else ""
            top_hour = best_hours[0][0] if best_hours else 0
            
            if top_day and top_hour is not None:
                am_pm = "AM" if top_hour < 12 else "PM"
                display_hour = top_hour if top_hour <= 12 else top_hour - 12
                display_hour = 12 if display_hour == 0 else display_hour
                insights.append(f"Optimal posting time: {top_day} at {display_hour} {am_pm} for maximum engagement.")
        
        return insights
    
    def generate_content_structure_insights(self) -> List[str]:
        """
        Generate insights about content structure.
        
        Returns:
            List of insight strings
        """
        insights = []
        content_insights = self.metrics.get('content_insights', {})
        
        if "error" in content_insights:
            return ["No content structure data available to analyze."]
        
        caption_analysis = content_insights.get('caption_length_analysis', {})
        video_analysis = content_insights.get('video_duration_analysis', {})
        
        # Caption length insights
        if caption_analysis:
            best_length = caption_analysis.get('best_performing_length', '')
            
            if best_length:
                insights.append(f"Captions with {best_length} length perform best in terms of engagement.")
                
                ranges = caption_analysis.get('ranges', {})
                if ranges:
                    for length_range, data in ranges.items():
                        if length_range == best_length:
                            insights.append(f"- {length_range} captions average {data.get('avg_engagement', 0):.1f} engagement per post.")
        
        # Video duration insights
        if video_analysis:
            best_duration = video_analysis.get('best_performing_duration', '')
            
            if best_duration:
                insights.append(f"Videos with {best_duration} duration perform best in terms of engagement.")
                
                ranges = video_analysis.get('ranges', {})
                if ranges:
                    for duration_range, data in ranges.items():
                        if duration_range == best_duration:
                            insights.append(f"- {duration_range} videos average {data.get('avg_engagement', 0):.1f} engagement and {data.get('avg_views', 0):.1f} views per video.")
        
        # Recommendations
        recommendations = []
        
        if caption_analysis and 'best_performing_length' in caption_analysis:
            best_length = caption_analysis['best_performing_length']
            recommendations.append(f"Optimize your captions to be {best_length} for maximum engagement.")
        
        if video_analysis and 'best_performing_duration' in video_analysis:
            best_duration = video_analysis['best_performing_duration']
            recommendations.append(f"Create videos that are {best_duration} to maximize engagement and views.")
        
        if recommendations:
            insights.append("Content structure recommendations:")
            insights.extend([f"- {rec}" for rec in recommendations])
        
        return insights
    
    def generate_sentiment_insights(self) -> List[str]:
        """
        Generate insights about comment sentiment.
        
        Returns:
            List of insight strings
        """
        insights = []
        sentiment_analysis = self.metrics.get('sentiment_analysis', {})
        
        if "error" in sentiment_analysis:
            return ["No sentiment data available to analyze."]
        
        total_comments = sentiment_analysis.get('total_comments_analyzed', 0)
        positive_percentage = sentiment_analysis.get('positive_percentage', 0)
        negative_percentage = sentiment_analysis.get('negative_percentage', 0)
        neutral_percentage = sentiment_analysis.get('neutral_percentage', 0)
        
        insights.append(f"Analysis of {total_comments} comments shows the following sentiment distribution:")
        insights.append(f"- Positive: {positive_percentage:.1f}%")
        insights.append(f"- Neutral: {neutral_percentage:.1f}%")
        insights.append(f"- Negative: {negative_percentage:.1f}%")
        
        # Overall sentiment assessment
        if positive_percentage > 60:
            insights.append("Your audience sentiment is predominantly positive, indicating strong content resonance.")
        elif positive_percentage > 40:
            insights.append("Your audience sentiment is moderately positive, with room for improvement.")
        else:
            insights.append("Your audience sentiment shows significant room for improvement. Consider addressing common concerns in comments.")
        
        # Content-specific sentiment
        content_sentiment = sentiment_analysis.get('content_sentiment', {})
        
        if content_sentiment:
            # Find content with highest positive sentiment
            most_positive_content = max(content_sentiment.items(), key=lambda x: x[1]['positive'] / max(x[1]['total'], 1) if x[1]['total'] > 0 else 0)
            content_id, sentiment_data = most_positive_content
            
            if sentiment_data['total'] > 0:
                positive_ratio = sentiment_data['positive'] / sentiment_data['total']
                if positive_ratio > 0.7:
                    # Find this content in the performance data
                    content_performance = self.metrics.get('content_performance', [])
                    content_info = next((c for c in content_performance if c.get('id') == content_id), None)
                    
                    if content_info:
                        caption = content_info.get('caption', '')
                        caption_preview = caption[:50] + "..." if len(caption) > 50 else caption
                        insights.append(f"Content with highest positive sentiment: '{caption_preview}' ({positive_ratio:.1%} positive comments)")
        
        return insights
    
    def generate_all_insights(self) -> Dict[str, List[str]]:
        """
        Generate all available insights.
        
        Returns:
            Dictionary containing all insights
        """
        return {
            "engagement_insights": self.generate_engagement_insights(),
            "content_performance_insights": self.generate_content_performance_insights(),
            "hashtag_insights": self.generate_hashtag_insights(),
            "mention_insights": self.generate_mention_insights(),
            "posting_time_insights": self.generate_posting_time_insights(),
            "content_structure_insights": self.generate_content_structure_insights(),
            "sentiment_insights": self.generate_sentiment_insights()
        }
    
    def generate_summary_insights(self) -> List[str]:
        """
        Generate a summary of the most important insights.
        
        Returns:
            List of summary insight strings
        """
        all_insights = self.generate_all_insights()
        
        # Extract key insights from each category
        summary = ["# Instagram Content Analysis Summary"]
        
        # Engagement summary
        engagement_insights = all_insights.get('engagement_insights', [])
        if engagement_insights:
            summary.append("\n## Engagement Overview")
            summary.append(engagement_insights[0] if len(engagement_insights) > 0 else "")
            if len(engagement_insights) > 1:
                summary.append(engagement_insights[1])
        
        # Content performance summary
        content_insights = all_insights.get('content_performance_insights', [])
        if content_insights:
            summary.append("\n## Top Performing Content")
            top_content_insights = [insight for insight in content_insights if "Your top performing content:" in insight or "Videos perform better" in insight or "Images/carousels perform better" in insight]
            summary.extend(top_content_insights)
        
        # Hashtag summary
        hashtag_insights = all_insights.get('hashtag_insights', [])
        if hashtag_insights:
            summary.append("\n## Hashtag Performance")
            hashtag_summary = [insight for insight in hashtag_insights if "Hashtags with highest engagement:" in insight or "Recommended hashtags" in insight]
            if hashtag_summary:
                summary.extend(hashtag_summary)
                # Add the top 3 hashtags if available
                for insight in hashtag_insights:
                    if insight.startswith("1. #"):
                        summary.append(insight)
                    if insight.startswith("2. #"):
                        summary.append(insight)
                    if insight.startswith("3. #"):
                        summary.append(insight)
        
        # Posting time summary
        posting_insights = all_insights.get('posting_time_insights', [])
        if posting_insights:
            summary.append("\n## Optimal Posting Strategy")
            optimal_time = [insight for insight in posting_insights if "Optimal posting time:" in insight]
            if optimal_time:
                summary.extend(optimal_time)
            else:
                best_times = [insight for insight in posting_insights if "Best times to post" in insight or "Best days to post" in insight]
                summary.extend(best_times[:2])
        
        # Content structure recommendations
        structure_insights = all_insights.get('content_structure_insights', [])
        if structure_insights:
            summary.append("\n## Content Structure Recommendations")
            recommendations = [insight for insight in structure_insights if "Content structure recommendations:" in insight or "Captions with" in insight or "Videos with" in insight]
            summary.extend(recommendations[:3])
        
        # Sentiment overview
        sentiment_insights = all_insights.get('sentiment_insights', [])
        if sentiment_insights:
            summary.append("\n## Audience Sentiment")
            sentiment_overview = [insight for insight in sentiment_insights if "Analysis of" in insight or "Your audience sentiment" in insight]
            summary.extend(sentiment_overview[:2])
        
        # Final recommendations
        summary.append("\n## Key Recommendations")
        
        # Collect recommendations from various sections
        recommendations = []
        
        # From content performance
        for insight in content_insights:
            if "perform better" in insight:
                content_type = "video" if "Videos perform better" in insight else "image/carousel"
                recommendations.append(f"- Focus on creating more {content_type} content as it generates higher engagement")
                break
        
        # From hashtags
        for insight in hashtag_insights:
            if "Recommended hashtags" in insight:
                recommendations.append("- Utilize the recommended hashtags to increase content reach and engagement")
                break
        
        # From posting time
        for insight in posting_insights:
            if "Optimal posting time:" in insight:
                recommendations.append(f"- {insight.replace('Optimal posting time: ', 'Post content on ')}")
                break
        
        # From content structure
        for insight in structure_insights:
            if "Optimize your captions" in insight or "Create videos that are" in insight:
                recommendations.append(f"- {insight}")
        
        # Add recommendations to summary
        summary.extend(recommendations)
        
        return summary


if __name__ == "__main__":
    # Example usage
    metadata_dir = "../data/metadata"
    videos_dir = "../data/videos"
    
    insights_generator = InstagramInsightsGenerator(metadata_dir=metadata_dir, videos_dir=videos_dir)
    summary_insights = insights_generator.generate_summary_insights()
    
    print("\n".join(summary_insights))
