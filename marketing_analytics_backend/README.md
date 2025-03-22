# Marketing Analytics Backend

A multi-modal marketing analytics tool that uses Google Gemini to analyze social media content metadata and videos to provide aggregated insights for businesses. Now with Supabase integration for simplified database management.

## Project Overview

This backend service provides:

- Processing of social media content metadata and videos
- Storage of content data and metrics in Supabase
- AI-driven insights using Google Gemini
- RESTful API endpoints for accessing analytics and insights

## Project Structure

```
marketing_analytics_backend/
├── api/                      # API endpoints
│   └── routes.py             # Flask routes
├── config/                   # Configuration
│   └── settings.py           # App settings and environment variables
├── database/                 # Database integration
│   ├── models.py             # Legacy SQLAlchemy models
│   └── supabase_client.py    # Supabase client for database operations
├── gemini_integration/       # Google Gemini integration
│   └── client.py             # Gemini API client
├── analytics/                # Analytics and insights
│   └── sample_analytics.py   # Analytics processing
├── sample_data/              # Sample data handling
│   ├── generator.py          # Generate sample data
│   ├── processor.py          # Process sample data
│   └── cli.py                # CLI for sample data operations
├── data/                     # Data storage
│   ├── metadata/             # JSON metadata files
│   └── videos/               # Video files (.mp4)
├── utils/                    # Utility functions
├── tests/                    # Unit and integration tests
├── app.py                    # Main application file
└── requirements.txt          # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Supabase account and project
- Google Gemini API key

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd marketing_analytics_backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables (see `.env.example`)::
   ```
   # Supabase settings
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   
   # Google Gemini API
   GEMINI_API_KEY=your-gemini-api-key
   ```

5. Set up your Supabase project:
   - Create a new project in the Supabase dashboard
   - Create the following tables in the Supabase SQL editor:

   ```sql
   -- Create businesses table
   CREATE TABLE businesses (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     name TEXT NOT NULL,
     industry TEXT
   );

   -- Create social_accounts table
   CREATE TABLE social_accounts (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     business_id UUID REFERENCES businesses(id),
     platform TEXT NOT NULL,
     account_id TEXT NOT NULL,
     account_name TEXT NOT NULL
   );

   -- Create social_metrics table
   CREATE TABLE social_metrics (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     social_account_id UUID REFERENCES social_accounts(id),
     timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
     followers INTEGER,
     likes INTEGER,
     comments INTEGER,
     shares INTEGER,
     views INTEGER,
     platform_data JSONB
   );

   -- Create content table
   CREATE TABLE content (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     social_account_id UUID REFERENCES social_accounts(id),
     content_id TEXT NOT NULL,
     content_type TEXT,
     title TEXT,
     description TEXT,
     url TEXT,
     thumbnail_url TEXT,
     published_at TIMESTAMP WITH TIME ZONE,
     likes INTEGER,
     comments INTEGER,
     shares INTEGER,
     views INTEGER,
     content_metadata JSONB
   );

   -- Create insights table
   CREATE TABLE insights (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     business_id UUID REFERENCES businesses(id),
     insight_type TEXT NOT NULL,
     title TEXT NOT NULL,
     content TEXT NOT NULL,
     timestamp TIMESTAMP WITH TIME ZONE NOT NULL
   );
   ```

### Running the Application

1. Generate sample data:

```
python -m sample_data.cli generate --output-dir ./data --days 30
```

2. Load sample data into Supabase:

```
python -m sample_data.cli load --data-dir ./data
```

3. Process video content (if available):

```
python -m sample_data.cli process-videos --sample-dir ./data/videos --temp-dir ./temp
```

4. Run the application:

```
python app.py
```

The application will be available at http://localhost:5000.

## API Endpoints

### Business Management

- `GET /api/businesses` - Get all businesses
- `GET /api/businesses/<business_id>` - Get a specific business
- `POST /api/businesses` - Create a new business

### Social Account Management

- `GET /api/businesses/<business_id>/accounts` - Get all social accounts for a business
- `POST /api/businesses/<business_id>/accounts` - Create a new social account

### Data Processing

- `POST /api/process` - Process metadata and video files

### Analytics

- `POST /api/analyze` - Trigger analytics on stored data

### Insights

- `GET /api/insights` - Get insights for all businesses or a specific business
- `GET /api/insights/<insight_id>` - Get a specific insight

### Metrics and Content

- `GET /api/metrics` - Get metrics for social accounts
- `GET /api/content` - Get content for social accounts

## Integration with Google Gemini

The backend integrates with Google Gemini to provide AI-driven insights from social media content. The Gemini client is used to:

1. Analyze engagement trends based on content metadata
2. Identify product demand based on content analysis
3. Analyze video content for insights
4. Generate marketing recommendations

## Development Notes

- The Gemini integration in `gemini_integration/client.py` demonstrates how to structure prompts and parse responses for different types of insights.
- The `sample_data` module provides tools for generating and processing sample data.
- The `data` directory contains subdirectories for storing metadata JSON files and video files.

## Security Considerations

- API keys and secrets are stored in environment variables
- Supabase credentials are stored in environment variables
- Supabase provides built-in authentication and authorization capabilities that can be leveraged for a production deployment

## Future Enhancements

- User authentication and authorization
- More granular insights and analytics
- Export functionality for reports
- Dashboard integration
- Real-time data processing
