# Data Directory

This directory contains the social media content metadata and video files used for analytics.

## Structure

- `metadata/`: Contains JSON files with social media content metadata
- `videos/`: Contains video files (.mp4) for analysis

## Metadata Format

The metadata JSON files should follow this format (example for Instagram content):

```json
[
  {
    "url": "https://www.instagram.com/p/sample123/",
    "source": "instagram",
    "title": "Summer collection preview #fashion",
    "author": "fashionbrand",
    "shortcode": "sample123",
    "thumbnail": "https://instagram.fcdn.com/sample123.jpg",
    "duration": 30,
    "media": [
      {
        "id": "media_1",
        "url": "https://instagram.fcdn.com/media_1.mp4",
        "quality": "hd",
        "type": "video",
        "extension": "mp4"
      }
    ],
    "likes": 1250,
    "comments": 87,
    "views": 5600,
    "shares": 120,
    "published_at": "2025-03-15T14:30:00Z",
    "content_metadata": {
      "hashtags": ["fashion", "summer", "collection", "preview"],
      "mentions": ["@designer", "@model"],
      "location": "Los Angeles, CA",
      "product_tags": [
        {
          "name": "Summer Dress",
          "id": "prod123"
        }
      ],
      "music": {
        "title": "Summer Vibes",
        "artist": "DJ Cool"
      }
    }
  }
]
```

## Video Files

Place your video files (.mp4) in the `videos/` directory. The file names should match the media IDs in the metadata files to enable proper linking between metadata and video content.

## Usage

1. Place your metadata JSON files in the `metadata/` directory
2. Place your video files in the `videos/` directory
3. Use the CLI to process the data:

```bash
# Generate sample data (if you don't have your own)
python -m sample_data.cli generate --output-dir ./data --days 30

# Load data into Supabase
python -m sample_data.cli load --data-dir ./data

# Process videos
python -m sample_data.cli process-videos --sample-dir ./data/videos --temp-dir ./temp
```

## Notes

- The system will automatically detect and process new files added to these directories
- JSON files should be valid and follow the format shown above
- Video files should be in .mp4 format for best compatibility
