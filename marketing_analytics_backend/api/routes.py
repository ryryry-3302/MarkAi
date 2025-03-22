"""
API routes for the Marketing Analytics Backend.
Defines Flask routes for handling API requests.
"""
from flask import Blueprint, jsonify, request, current_app
from database.models import db, Business, SocialAccount, SocialMetric, Content, Insight
from analytics.sample_analytics import run_analytics
from sample_data.processor import process_instagram_content, process_video_content
import logging
import os
import json
from pathlib import Path

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
    businesses = Business.query.all()
    result = []
    
    for business in businesses:
        result.append({
            'id': business.id,
            'name': business.name,
            'industry': business.industry,
            'created_at': business.created_at.isoformat()
        })
    
    return jsonify(result)

@api_bp.route('/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    """Get a specific business by ID."""
    business = Business.query.get_or_404(business_id)
    
    # Get social accounts for the business
    accounts = []
    for account in business.social_accounts:
        accounts.append({
            'id': account.id,
            'platform': account.platform,
            'account_name': account.account_name
        })
    
    result = {
        'id': business.id,
        'name': business.name,
        'industry': business.industry,
        'created_at': business.created_at.isoformat(),
        'social_accounts': accounts
    }
    
    return jsonify(result)

@api_bp.route('/businesses', methods=['POST'])
def create_business():
    """Create a new business."""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    business = Business(
        name=data['name'],
        industry=data.get('industry')
    )
    
    db.session.add(business)
    db.session.commit()
    
    return jsonify({
        'id': business.id,
        'name': business.name,
        'industry': business.industry,
        'created_at': business.created_at.isoformat()
    }), 201

# Social account endpoints
@api_bp.route('/businesses/<int:business_id>/accounts', methods=['GET'])
def get_social_accounts(business_id):
    """Get all social accounts for a business."""
    Business.query.get_or_404(business_id)
    accounts = SocialAccount.query.filter_by(business_id=business_id).all()
    
    result = []
    for account in accounts:
        result.append({
            'id': account.id,
            'platform': account.platform,
            'account_id': account.account_id,
            'account_name': account.account_name,
            'created_at': account.created_at.isoformat()
        })
    
    return jsonify(result)

@api_bp.route('/businesses/<int:business_id>/accounts', methods=['POST'])
def create_social_account(business_id):
    """Create a new social account for a business."""
    Business.query.get_or_404(business_id)
    data = request.json
    
    if not data or 'platform' not in data or 'account_id' not in data:
        return jsonify({'error': 'Platform and account_id are required'}), 400
    
    account = SocialAccount(
        business_id=business_id,
        platform=data['platform'],
        account_id=data['account_id'],
        account_name=data.get('account_name')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'id': account.id,
        'platform': account.platform,
        'account_id': account.account_id,
        'account_name': account.account_name,
        'created_at': account.created_at.isoformat()
    }), 201

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
        
        # Process Instagram content files
        if content_type == 'all' or content_type == 'instagram':
            for file_path in metadata_path.glob('*.json'):
                with open(file_path, 'r') as f:
                    content_data = json.load(f)
                    process_instagram_content(content_data)
                    processed_files.append(str(file_path))
        
        # Process video files
        if content_type == 'all' or content_type == 'video':
            for file_path in videos_path.glob('*.mp4'):
                process_video_content(str(file_path))
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
        run_analytics()
        return jsonify({'message': 'Analytics process initiated'})
    
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
    
    query = Insight.query
    
    if business_id:
        query = query.filter_by(business_id=business_id)
    
    if insight_type:
        query = query.filter_by(insight_type=insight_type)
    
    insights = query.order_by(Insight.generated_at.desc()).limit(limit).all()
    
    result = []
    for insight in insights:
        result.append({
            'id': insight.id,
            'business_id': insight.business_id,
            'insight_type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'confidence_score': insight.confidence_score,
            'generated_at': insight.generated_at.isoformat(),
            'data': insight.get_raw_data()
        })
    
    return jsonify(result)

@api_bp.route('/insights/<int:insight_id>', methods=['GET'])
def get_insight(insight_id):
    """Get a specific insight by ID."""
    insight = Insight.query.get_or_404(insight_id)
    
    result = {
        'id': insight.id,
        'business_id': insight.business_id,
        'insight_type': insight.insight_type,
        'title': insight.title,
        'description': insight.description,
        'confidence_score': insight.confidence_score,
        'generated_at': insight.generated_at.isoformat(),
        'data': insight.get_raw_data()
    }
    
    return jsonify(result)

# Metrics endpoints
@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get metrics for a specific social account."""
    account_id = request.args.get('account_id')
    platform = request.args.get('platform')
    business_id = request.args.get('business_id')
    limit = request.args.get('limit', 30, type=int)
    
    query = SocialMetric.query.join(SocialAccount)
    
    if account_id:
        query = query.filter(SocialAccount.id == account_id)
    
    if platform:
        query = query.filter(SocialAccount.platform == platform)
    
    if business_id:
        query = query.filter(SocialAccount.business_id == business_id)
    
    metrics = query.order_by(SocialMetric.timestamp.desc()).limit(limit).all()
    
    result = []
    for metric in metrics:
        account = metric.social_account
        result.append({
            'id': metric.id,
            'account_id': account.id,
            'platform': account.platform,
            'account_name': account.account_name,
            'timestamp': metric.timestamp.isoformat(),
            'followers': metric.followers,
            'likes': metric.likes,
            'comments': metric.comments,
            'shares': metric.shares,
            'views': metric.views,
            'platform_data': metric.get_platform_data()
        })
    
    return jsonify(result)

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
