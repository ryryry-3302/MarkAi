"""
API routes for the Marketing Analytics Backend.
Defines Flask routes for handling API requests.
"""
from flask import Blueprint, jsonify, request, current_app
from database.supabase_client import get_supabase_client
from analytics.sample_analytics import run_analytics
from sample_data.instagram_processor import process_instagram_content, process_video_content
import logging
import os
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_routes(app):
    """Register all blueprints with the app."""
    app.register_blueprint(api_bp)

# Business endpoints
@api_bp.route('/businesses', methods=['GET'])
def get_businesses():
    """Get all businesses."""
    supabase = get_supabase_client()
    businesses = supabase.get_businesses()
    
    return jsonify(businesses)

@api_bp.route('/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    """Get a specific business by ID."""
    supabase = get_supabase_client()
    business = supabase.get_business(business_id)
    
    if not business:
        return jsonify({'error': 'Business not found'}), 404
    
    # Get social accounts for the business
    accounts = supabase.get_social_accounts(business_id)
    
    result = {
        'id': business['id'],
        'name': business['name'],
        'industry': business['industry'],
        'created_at': business.get('created_at', datetime.now().isoformat()),
        'social_accounts': accounts
    }
    
    return jsonify(result)

@api_bp.route('/businesses', methods=['POST'])
def create_business():
    """Create a new business."""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    supabase = get_supabase_client()
    business = supabase.create_business(
        name=data['name'],
        industry=data.get('industry', 'Other')
    )
    
    if not business:
        return jsonify({'error': 'Failed to create business'}), 500
    
    return jsonify(business), 201

# Social account endpoints
@api_bp.route('/businesses/<int:business_id>/accounts', methods=['GET'])
def get_social_accounts(business_id):
    """Get all social accounts for a business."""
    supabase = get_supabase_client()
    business = supabase.get_business(business_id)
    
    if not business:
        return jsonify({'error': 'Business not found'}), 404
        
    accounts = supabase.get_social_accounts(business_id)
    
    return jsonify(accounts)

@api_bp.route('/businesses/<int:business_id>/accounts', methods=['POST'])
def create_social_account(business_id):
    """Create a new social account for a business."""
    supabase = get_supabase_client()
    business = supabase.get_business(business_id)
    
    if not business:
        return jsonify({'error': 'Business not found'}), 404
        
    data = request.json
    
    if not data or 'platform' not in data or 'account_id' not in data:
        return jsonify({'error': 'Platform and account_id are required'}), 400
    
    account = supabase.create_social_account(
        business_id=business_id,
        platform=data['platform'],
        account_id=data['account_id'],
        account_name=data.get('account_name')
    )
    
    if not account:
        return jsonify({'error': 'Failed to create social account'}), 500
    
    return jsonify(account), 201

# Data processing endpoints
@api_bp.route('/process', methods=['POST'])
def process_data():
    """Process local metadata and video files."""
    try:
        data = request.get_json() or {}
        content_type = data.get('content_type', 'all')
        metadata_dir = data.get('metadata_dir', 'data/metadata')
        videos_dir = data.get('videos_dir', 'data/videos')
        
        # Ensure directories exist
        metadata_path = Path(metadata_dir)
        videos_path = Path(videos_dir)
        
        if not metadata_path.exists() or not videos_path.exists():
            return jsonify({'error': 'Metadata or videos directory not found'}), 404
        
        processed_files = []
        supabase = get_supabase_client()
        
        # Process Instagram content files
        if content_type == 'all' or content_type == 'instagram':
            for file_path in metadata_path.glob('*.json'):
                with open(file_path, 'r') as f:
                    content_data = json.load(f)
                    processed_content = process_instagram_content(content_data)
                    if processed_content:
                        # Store processed content in Supabase
                        supabase.store_content(processed_content)
                    processed_files.append(str(file_path))
        
        # Process video files
        if content_type == 'all' or content_type == 'video':
            for file_path in videos_path.glob('*.mp4'):
                processed_video = process_video_content(str(file_path))
                if processed_video:
                    # Store processed video in Supabase
                    supabase.store_content(processed_video)
                processed_files.append(str(file_path))
        
        return jsonify({
            'message': 'Data processing completed successfully',
            'processed_files': processed_files
        }), 200
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Analytics endpoints
@api_bp.route('/analyze', methods=['POST'])
def analyze_data():
    """Trigger analytics on stored data."""
    data = request.json or {}
    business_id = data.get('business_id')
    
    try:
        supabase = get_supabase_client()
        # Get content from Supabase for analysis
        contents = supabase.get_contents(business_id)
        
        if not contents:
            return jsonify({'message': 'No content found for analysis'}), 404
            
        # Run analytics on the retrieved content
        insights = run_analytics(contents)
        
        # Store insights in Supabase
        if insights:
            for insight in insights:
                supabase.store_insight(insight)
                
        return jsonify({
            'message': 'Analytics process completed',
            'insights_count': len(insights) if insights else 0
        })
    
    except Exception as e:
        logger.error(f"Error running analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Insights endpoints
@api_bp.route('/insights', methods=['GET'])
def get_insights():
    """Get insights for all businesses or a specific business."""
    business_id = request.args.get('business_id')
    insight_type = request.args.get('type')
    limit = request.args.get('limit', 10, type=int)
    
    supabase = get_supabase_client()
    insights = supabase.get_insights(business_id, insight_type, limit)
    
    return jsonify(insights)

@api_bp.route('/insights/<int:insight_id>', methods=['GET'])
def get_insight(insight_id):
    """Get a specific insight by ID."""
    supabase = get_supabase_client()
    insight = supabase.get_insight(insight_id)
    
    if not insight:
        return jsonify({'error': 'Insight not found'}), 404
    
    return jsonify(insight)

# Metrics endpoints
@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get metrics for a specific social account."""
    account_id = request.args.get('account_id')
    platform = request.args.get('platform')
    business_id = request.args.get('business_id')
    limit = request.args.get('limit', 30, type=int)
    
    supabase = get_supabase_client()
    metrics = supabase.get_metrics(account_id, platform, business_id, limit)
    
    return jsonify(metrics)

# Content endpoints
@api_bp.route('/content', methods=['GET'])
def get_content():
    """Get content for a specific social account."""
    account_id = request.args.get('account_id')
    platform = request.args.get('platform')
    business_id = request.args.get('business_id')
    content_type = request.args.get('content_type')
    limit = request.args.get('limit', 30, type=int)
    
    query = Content.query.join(SocialAccount)
    
    if account_id:
        query = query.filter(SocialAccount.id == account_id)
    
    if platform:
        query = query.filter(SocialAccount.platform == platform)
    
    if business_id:
        query = query.filter(SocialAccount.business_id == business_id)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    content_items = query.order_by(Content.published_at.desc()).limit(limit).all()
    
    result = []
    for item in content_items:
        account = item.social_account
        result.append({
            'id': item.id,
            'account_id': account.id,
            'platform': account.platform,
            'account_name': account.account_name,
            'content_id': item.content_id,
            'content_type': item.content_type,
            'title': item.title,
            'description': item.description,
            'url': item.url,
            'thumbnail_url': item.thumbnail_url,
            'published_at': item.published_at.isoformat(),
            'likes': item.likes,
            'comments': item.comments,
            'shares': item.shares,
            'views': item.views,
            'metadata': item.get_content_metadata()
        })
    
    return jsonify(result)
