"""
Google Gemini integration for analyzing video content.
"""
import google.generativeai as genai
import base64
import logging
import json
import os
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

class GeminiVideoAnalyzer:
    """Client for analyzing video content with Google Gemini."""
    
    def __init__(self, api_key):
        """Initialize the Gemini client with API key."""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Use gemini-pro-vision for image/video analysis
        self.model = genai.GenerativeModel('gemini-pro-vision')
    
    def analyze_video_content(self, video_data, content_info):
        """
        Analyze video content using key frames and metadata.
        
        Args:
            video_data: Dictionary containing video metadata and frame paths
            content_info: Dictionary containing content information (title, description, etc.)
            
        Returns:
            Dictionary containing video content analysis
        """
        try:
            # Load video frames as images
            frame_images = []
            for frame_path in video_data.get('frame_paths', []):
                # In a real implementation, you would load actual images
                # For this example, we'll use placeholder data if the file doesn't exist
                try:
                    if os.path.exists(frame_path):
                        img = Image.open(frame_path)
                        frame_images.append(img)
                except Exception as e:
                    logger.warning(f"Could not load frame {frame_path}: {str(e)}")
            
            # If no frames were loaded, we can't analyze the video
            if not frame_images:
                logger.warning("No frames loaded for video analysis")
                return {
                    "error": "No frames available for analysis",
                    "content_id": content_info.get('content_id')
                }
            
            # Create prompt for Gemini
            prompt = self._create_video_analysis_prompt(video_data, content_info)
            
            # Generate content with images and prompt
            response = self.model.generate_content([prompt, *frame_images])
            
            # Parse and structure the response
            analysis = self._parse_video_analysis(response.text)
            
            return {
                "content_id": content_info.get('content_id'),
                "platform": content_info.get('platform'),
                "content_type": content_info.get('content_type'),
                "analysis": analysis,
                "raw_response": response.text
            }
        
        except Exception as e:
            logger.error(f"Error analyzing video content: {str(e)}")
            return {
                "error": str(e),
                "content_id": content_info.get('content_id')
            }
    
    def analyze_video_batch(self, video_data_batch, content_info_batch):
        """
        Analyze a batch of videos.
        
        Args:
            video_data_batch: Dictionary mapping content IDs to video data
            content_info_batch: Dictionary mapping content IDs to content info
            
        Returns:
            List of video analysis results
        """
        results = []
        
        for content_id, video_data in video_data_batch.items():
            if content_id in content_info_batch:
                content_info = content_info_batch[content_id]
                result = self.analyze_video_content(video_data, content_info)
                results.append(result)
        
        return results
    
    def _create_video_analysis_prompt(self, video_data, content_info):
        """Create a prompt for video content analysis."""
        metadata = video_data.get('metadata', {})
        
        prompt = f"""
        You are an expert marketing analyst. Analyze the following video content from {content_info.get('platform', 'social media')}.
        I'm showing you key frames from a {content_info.get('content_type', 'video')}.
        
        VIDEO INFORMATION:
        Title: {content_info.get('title', 'Unknown')}
        Description: {content_info.get('description', 'No description')}
        Platform: {content_info.get('platform', 'Unknown')}
        Content Type: {content_info.get('content_type', 'video')}
        Duration: {metadata.get('duration', 'Unknown')} seconds
        Resolution: {metadata.get('width', 'Unknown')}x{metadata.get('height', 'Unknown')}
        
        Based on the key frames and information provided, analyze the following aspects:
        1. Visual content and quality
        2. Brand presence and product visibility
        3. Marketing effectiveness
        4. Target audience appeal
        5. Engagement potential
        6. Improvement suggestions
        
        Format your response as JSON with the following structure:
        {{
            "visual_analysis": {{
                "quality": "description of visual quality",
                "composition": "description of visual composition",
                "color_scheme": "description of color scheme",
                "key_elements": ["list", "of", "key", "visual", "elements"]
            }},
            "brand_analysis": {{
                "brand_presence": "description of brand presence",
                "product_visibility": "description of product visibility",
                "key_products": ["list", "of", "visible", "products"],
                "brand_consistency": "assessment of brand consistency"
            }},
            "marketing_effectiveness": {{
                "message_clarity": "assessment of message clarity",
                "call_to_action": "description of call to action if present",
                "unique_selling_points": ["list", "of", "unique", "selling", "points"],
                "overall_effectiveness": "overall assessment of marketing effectiveness"
            }},
            "audience_appeal": {{
                "target_demographic": ["list", "of", "likely", "target", "demographics"],
                "emotional_appeal": "description of emotional appeal",
                "relevance": "assessment of content relevance to target audience"
            }},
            "engagement_potential": {{
                "virality_factors": ["list", "of", "factors", "that", "could", "drive", "virality"],
                "comment_triggers": ["list", "of", "elements", "likely", "to", "trigger", "comments"],
                "share_worthiness": "assessment of share-worthiness",
                "predicted_engagement": "high/medium/low with brief explanation"
            }},
            "improvement_suggestions": ["list", "of", "actionable", "suggestions", "for", "improvement"]
        }}
        """
        
        return prompt
    
    def _parse_video_analysis(self, response_text):
        """Parse video analysis from Gemini response."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, return a structured version of the text
            return {
                "visual_analysis": {
                    "quality": "Unable to parse structured analysis",
                    "key_elements": []
                },
                "raw_text": response_text[:500]  # Truncate long text
            }
        
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Gemini response")
            return {
                "parsing_error": True,
                "raw_text": response_text[:500]  # Truncate long text
            }
