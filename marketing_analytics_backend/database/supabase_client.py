"""
Supabase client for the marketing analytics backend.
Handles database operations using the Supabase API.
"""
import os
import json
import logging
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """Client for interacting with Supabase."""
    
    def __init__(self):
        """Initialize the Supabase client with credentials from environment variables."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be set in environment variables")
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client initialized")
    
    def get_businesses(self):
        """Get all businesses."""
        response = self.client.table("businesses").select("*").execute()
        return response.data
    
    def get_business(self, business_id):
        """Get a business by ID."""
        response = self.client.table("businesses").select("*").eq("id", business_id).execute()
        if response.data:
            return response.data[0]
        return None
    
    def create_business(self, name, industry):
        """Create a new business."""
        response = self.client.table("businesses").insert({
            "name": name,
            "industry": industry
        }).execute()
        return response.data[0] if response.data else None
    
    def update_business(self, business_id, data):
        """Update a business."""
        response = self.client.table("businesses").update(data).eq("id", business_id).execute()
        return response.data[0] if response.data else None
    
    def delete_business(self, business_id):
        """Delete a business."""
        response = self.client.table("businesses").delete().eq("id", business_id).execute()
        return response.data
    
    def get_social_accounts(self, business_id=None):
        """Get social accounts, optionally filtered by business ID."""
        query = self.client.table("social_accounts").select("*")
        if business_id:
            query = query.eq("business_id", business_id)
        response = query.execute()
        return response.data
    
    def get_social_account(self, account_id):
        """Get a social account by ID."""
        response = self.client.table("social_accounts").select("*").eq("id", account_id).execute()
        if response.data:
            return response.data[0]
        return None
    
    def create_social_account(self, business_id, platform, account_id, account_name):
        """Create a new social account."""
        response = self.client.table("social_accounts").insert({
            "business_id": business_id,
            "platform": platform,
            "account_id": account_id,
            "account_name": account_name
        }).execute()
        return response.data[0] if response.data else None
    
    def update_social_account(self, account_id, data):
        """Update a social account."""
        response = self.client.table("social_accounts").update(data).eq("id", account_id).execute()
        return response.data[0] if response.data else None
    
    def delete_social_account(self, account_id):
        """Delete a social account."""
        response = self.client.table("social_accounts").delete().eq("id", account_id).execute()
        return response.data
    
    def get_metrics(self, account_id=None, start_date=None, end_date=None):
        """Get metrics, optionally filtered by account ID and date range."""
        query = self.client.table("social_metrics").select("*")
        
        if account_id:
            query = query.eq("social_account_id", account_id)
        
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
        
        response = query.execute()
        return response.data
    
    def create_metric(self, social_account_id, timestamp, followers, likes, comments, shares, views, platform_data):
        """Create a new metric."""
        response = self.client.table("social_metrics").insert({
            "social_account_id": social_account_id,
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            "followers": followers,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "platform_data": json.dumps(platform_data) if platform_data else None
        }).execute()
        return response.data[0] if response.data else None
    
    def get_content(self, account_id=None, content_type=None, start_date=None, end_date=None):
        """Get content, optionally filtered by account ID, content type, and date range."""
        query = self.client.table("content").select("*")
        
        if account_id:
            query = query.eq("social_account_id", account_id)
        
        if content_type:
            query = query.eq("content_type", content_type)
        
        if start_date:
            query = query.gte("published_at", start_date.isoformat())
        
        if end_date:
            query = query.lte("published_at", end_date.isoformat())
        
        response = query.execute()
        return response.data
    
    def get_content_item(self, content_id):
        """Get a content item by ID."""
        response = self.client.table("content").select("*").eq("id", content_id).execute()
        if response.data:
            return response.data[0]
        return None
    
    def create_content(self, social_account_id, content_id, content_type, title, description, url, 
                      thumbnail_url, published_at, likes, comments, shares, views, content_metadata):
        """Create a new content item."""
        response = self.client.table("content").insert({
            "social_account_id": social_account_id,
            "content_id": content_id,
            "content_type": content_type,
            "title": title,
            "description": description,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "published_at": published_at.isoformat() if isinstance(published_at, datetime) else published_at,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "content_metadata": json.dumps(content_metadata) if content_metadata else None
        }).execute()
        return response.data[0] if response.data else None
    
    def get_insights(self, business_id=None, insight_type=None):
        """Get insights, optionally filtered by business ID and insight type."""
        query = self.client.table("insights").select("*")
        
        if business_id:
            query = query.eq("business_id", business_id)
        
        if insight_type:
            query = query.eq("insight_type", insight_type)
        
        response = query.execute()
        return response.data
    
    def create_insight(self, business_id, insight_type, title, content):
        """Create a new insight."""
        response = self.client.table("insights").insert({
            "business_id": business_id,
            "insight_type": insight_type,
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    
    def bulk_insert(self, table_name, data_list):
        """Insert multiple records into a table."""
        if not data_list:
            return []
        
        # Process data to ensure JSON fields are properly serialized
        processed_data = []
        for item in data_list:
            processed_item = {}
            for key, value in item.items():
                if key in ["platform_data", "content_metadata"] and value is not None:
                    processed_item[key] = json.dumps(value)
                elif key in ["timestamp", "published_at"] and isinstance(value, datetime):
                    processed_item[key] = value.isoformat()
                else:
                    processed_item[key] = value
            processed_data.append(processed_item)
        
        # Insert data in batches to avoid request size limits
        batch_size = 100
        results = []
        
        for i in range(0, len(processed_data), batch_size):
            batch = processed_data[i:i+batch_size]
            response = self.client.table(table_name).insert(batch).execute()
            if response.data:
                results.extend(response.data)
        
        return results
    
    def load_sample_data(self, data):
        """
        Load sample data into Supabase.
        
        Args:
            data: Dictionary containing sample data for businesses, social_accounts, metrics, and content
        """
        try:
            # Clear existing data
            self.client.table("insights").delete().execute()
            self.client.table("content").delete().execute()
            self.client.table("social_metrics").delete().execute()
            self.client.table("social_accounts").delete().execute()
            self.client.table("businesses").delete().execute()
            
            # Load businesses
            businesses_result = self.bulk_insert("businesses", data.get("businesses", []))
            logger.info(f"Loaded {len(businesses_result)} businesses")
            
            # Load social accounts
            accounts_result = self.bulk_insert("social_accounts", data.get("social_accounts", []))
            logger.info(f"Loaded {len(accounts_result)} social accounts")
            
            # Load metrics
            metrics_result = self.bulk_insert("social_metrics", data.get("metrics", []))
            logger.info(f"Loaded {len(metrics_result)} metrics")
            
            # Load content
            content_result = self.bulk_insert("content", data.get("content", []))
            logger.info(f"Loaded {len(content_result)} content items")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading sample data: {str(e)}")
            return False
