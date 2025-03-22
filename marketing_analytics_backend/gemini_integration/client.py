"""
Google Gemini client for generating AI-driven insights from social media data.
"""
import google.generativeai as genai
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key):
        """Initialize the Gemini client with API key."""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_engagement_trends(self, metrics_data, content_data, business_name):
        """
        Analyze engagement trends from social media metrics.
        
        Args:
            metrics_data: List of social metrics records with platform data
            content_data: List of content records with engagement data
            business_name: Name of the business
            
        Returns:
            Dictionary containing engagement trend insights
        """
        try:
            # Prepare data for Gemini
            prompt = self._create_engagement_prompt(metrics_data, content_data, business_name)
            
            # Generate insights
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            insights = self._parse_engagement_insights(response.text)
            
            return {
                'type': 'engagement_trends',
                'title': f'Engagement Trends for {business_name}',
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat(),
                'confidence_score': 0.85,  # Placeholder, would be derived from Gemini's response
                'raw_response': response.text
            }
        
        except Exception as e:
            logger.error(f"Error analyzing engagement trends: {str(e)}")
            raise
    
    def analyze_product_demand(self, content_data, business_name, industry):
        """
        Analyze product demand based on social media content.
        
        Args:
            content_data: List of content records with engagement data
            business_name: Name of the business
            industry: Industry of the business
            
        Returns:
            Dictionary containing product demand insights
        """
        try:
            # Prepare data for Gemini
            prompt = self._create_product_demand_prompt(content_data, business_name, industry)
            
            # Generate insights
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            insights = self._parse_product_insights(response.text)
            
            return {
                'type': 'product_demand',
                'title': f'Product Demand Analysis for {business_name}',
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat(),
                'confidence_score': 0.8,  # Placeholder
                'raw_response': response.text
            }
        
        except Exception as e:
            logger.error(f"Error analyzing product demand: {str(e)}")
            raise
    
    def analyze_competitive_landscape(self, business_data, competitor_data, industry):
        """
        Analyze competitive landscape based on business and competitor data.
        
        Args:
            business_data: Dictionary containing business metrics and content
            competitor_data: List of dictionaries containing competitor metrics and content
            industry: Industry of the business
            
        Returns:
            Dictionary containing competitive landscape insights
        """
        try:
            # Prepare data for Gemini
            prompt = self._create_competitive_prompt(business_data, competitor_data, industry)
            
            # Generate insights
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            insights = self._parse_competitive_insights(response.text)
            
            return {
                'type': 'competitive_landscape',
                'title': 'Competitive Landscape Analysis',
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat(),
                'confidence_score': 0.75,  # Placeholder
                'raw_response': response.text
            }
        
        except Exception as e:
            logger.error(f"Error analyzing competitive landscape: {str(e)}")
            raise
    
    def generate_marketing_recommendations(self, all_insights, business_name, industry):
        """
        Generate marketing recommendations based on all insights.
        
        Args:
            all_insights: List of all generated insights
            business_name: Name of the business
            industry: Industry of the business
            
        Returns:
            Dictionary containing marketing recommendations
        """
        try:
            # Prepare data for Gemini
            prompt = self._create_recommendations_prompt(all_insights, business_name, industry)
            
            # Generate insights
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            recommendations = self._parse_recommendations(response.text)
            
            return {
                'type': 'marketing_recommendations',
                'title': f'Marketing Recommendations for {business_name}',
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat(),
                'confidence_score': 0.85,  # Placeholder
                'raw_response': response.text
            }
        
        except Exception as e:
            logger.error(f"Error generating marketing recommendations: {str(e)}")
            raise
    
    def _create_engagement_prompt(self, metrics_data, content_data, business_name):
        """Create a prompt for engagement trend analysis."""
        # Convert data to JSON strings for the prompt
        metrics_json = json.dumps(metrics_data, default=str)
        content_json = json.dumps(content_data, default=str)
        
        prompt = f"""
        You are an expert social media analyst. Analyze the following social media metrics and content data for {business_name}.
        
        METRICS DATA:
        {metrics_json}
        
        CONTENT DATA:
        {content_json}
        
        Based on this data, provide insights on:
        1. Overall engagement trends across platforms
        2. Which platform is performing best and why
        3. Types of content driving the most engagement
        4. Best days and times for posting
        5. Any concerning drops in engagement
        
        Format your response as JSON with the following structure:
        {{
            "overall_trend": "string describing the overall engagement trend",
            "best_platform": "name of best performing platform",
            "best_content_types": ["list", "of", "content", "types"],
            "optimal_posting_times": {{
                "days": ["list", "of", "best", "days"],
                "times": ["list", "of", "best", "times"]
            }},
            "engagement_concerns": "description of any concerning trends",
            "recommendations": ["list", "of", "actionable", "recommendations"]
        }}
        """
        
        return prompt
    
    def _create_product_demand_prompt(self, content_data, business_name, industry):
        """Create a prompt for product demand analysis."""
        # Convert data to JSON string for the prompt
        content_json = json.dumps(content_data, default=str)
        
        prompt = f"""
        You are an expert market analyst for the {industry} industry. Analyze the following social media content data for {business_name}.
        
        CONTENT DATA:
        {content_json}
        
        Based on this data, provide insights on:
        1. Which products or services are generating the most interest
        2. Emerging trends or potential new product opportunities
        3. Products or services that may be declining in popularity
        4. Seasonal patterns in product interest
        5. Customer sentiment towards different products
        
        Format your response as JSON with the following structure:
        {{
            "top_products": ["list", "of", "most", "popular", "products"],
            "emerging_trends": ["list", "of", "emerging", "trends"],
            "declining_products": ["list", "of", "declining", "products"],
            "seasonal_patterns": "description of any seasonal patterns",
            "sentiment_analysis": {{
                "product1": "sentiment description",
                "product2": "sentiment description"
            }},
            "recommendations": ["list", "of", "actionable", "recommendations"]
        }}
        """
        
        return prompt
    
    def _create_competitive_prompt(self, business_data, competitor_data, industry):
        """Create a prompt for competitive landscape analysis."""
        # Convert data to JSON strings for the prompt
        business_json = json.dumps(business_data, default=str)
        competitor_json = json.dumps(competitor_data, default=str)
        
        prompt = f"""
        You are an expert competitive analyst for the {industry} industry. Compare the following data for a business and its competitors.
        
        BUSINESS DATA:
        {business_json}
        
        COMPETITOR DATA:
        {competitor_json}
        
        Based on this data, provide insights on:
        1. How the business compares to competitors in terms of engagement
        2. Competitive advantages and disadvantages
        3. Gaps in the market that the business could exploit
        4. Threats from competitors
        5. Pricing strategy recommendations based on competitor activity
        
        Format your response as JSON with the following structure:
        {{
            "competitive_position": "description of overall position",
            "advantages": ["list", "of", "competitive", "advantages"],
            "disadvantages": ["list", "of", "competitive", "disadvantages"],
            "market_gaps": ["list", "of", "market", "gaps"],
            "threats": ["list", "of", "competitive", "threats"],
            "pricing_recommendations": "pricing strategy recommendations",
            "action_items": ["list", "of", "actionable", "recommendations"]
        }}
        """
        
        return prompt
    
    def _create_recommendations_prompt(self, all_insights, business_name, industry):
        """Create a prompt for marketing recommendations."""
        # Convert data to JSON string for the prompt
        insights_json = json.dumps(all_insights, default=str)
        
        prompt = f"""
        You are an expert marketing strategist for the {industry} industry. Based on the following insights for {business_name}, provide comprehensive marketing recommendations.
        
        INSIGHTS:
        {insights_json}
        
        Provide detailed marketing recommendations covering:
        1. Content strategy for each platform
        2. Advertising budget allocation
        3. Product promotion priorities
        4. Audience targeting suggestions
        5. Campaign ideas for the next quarter
        6. Key performance indicators to track
        
        Format your response as JSON with the following structure:
        {{
            "content_strategy": {{
                "platform1": "strategy description",
                "platform2": "strategy description"
            }},
            "budget_allocation": {{
                "platform1": "percentage",
                "platform2": "percentage"
            }},
            "product_priorities": ["list", "of", "products", "in", "priority", "order"],
            "audience_targeting": ["list", "of", "audience", "segments"],
            "campaign_ideas": [
                {{
                    "name": "campaign name",
                    "description": "campaign description",
                    "platforms": ["list", "of", "platforms"],
                    "timeline": "suggested timeline"
                }}
            ],
            "kpis": ["list", "of", "key", "performance", "indicators"]
        }}
        """
        
        return prompt
    
    def _parse_engagement_insights(self, response_text):
        """Parse engagement insights from Gemini response."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, return a structured version of the text
            return {
                'overall_trend': response_text,
                'best_platform': '',
                'best_content_types': [],
                'optimal_posting_times': {
                    'days': [],
                    'times': []
                },
                'engagement_concerns': '',
                'recommendations': []
            }
        
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Gemini response")
            return {
                'overall_trend': response_text[:500],  # Truncate long text
                'parsing_error': True
            }
    
    def _parse_product_insights(self, response_text):
        """Parse product insights from Gemini response."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, return a structured version of the text
            return {
                'top_products': [],
                'emerging_trends': [],
                'declining_products': [],
                'seasonal_patterns': response_text,
                'sentiment_analysis': {},
                'recommendations': []
            }
        
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Gemini response")
            return {
                'parsing_error': True,
                'raw_text': response_text[:500]  # Truncate long text
            }
    
    def _parse_competitive_insights(self, response_text):
        """Parse competitive insights from Gemini response."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, return a structured version of the text
            return {
                'competitive_position': response_text,
                'advantages': [],
                'disadvantages': [],
                'market_gaps': [],
                'threats': [],
                'pricing_recommendations': '',
                'action_items': []
            }
        
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Gemini response")
            return {
                'parsing_error': True,
                'raw_text': response_text[:500]  # Truncate long text
            }
    
    def _parse_recommendations(self, response_text):
        """Parse marketing recommendations from Gemini response."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, return a structured version of the text
            return {
                'content_strategy': {},
                'budget_allocation': {},
                'product_priorities': [],
                'audience_targeting': [],
                'campaign_ideas': [],
                'kpis': []
            }
        
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Gemini response")
            return {
                'parsing_error': True,
                'raw_text': response_text[:500]  # Truncate long text
            }
