"""
Sample data generator for marketing analytics.
Generates sample JSON data for social media metrics and content.
"""
import json
import random
import os
from datetime import datetime, timedelta
import uuid

# Sample business data
BUSINESSES = [
    {"id": 1, "name": "Los Pollos Tacos", "industry": "Restaurant"},
    {"id": 2, "name": "Urban Fitness", "industry": "Fitness"},
    {"id": 3, "name": "Tech Gadgets", "industry": "Retail"}
]

# Sample social media platforms
PLATFORMS = ["instagram", "youtube", "tiktok"]

# Sample content types
CONTENT_TYPES = {
    "instagram": ["post", "reel", "story"],
    "youtube": ["video", "short"],
    "tiktok": ["video"]
}

# Sample hashtags by industry
HASHTAGS = {
    "Restaurant": ["#food", "#foodie", "#delicious", "#yummy", "#instafood", "#dinner", "#lunch", "#tacos", "#mexicanfood"],
    "Fitness": ["#fitness", "#workout", "#gym", "#fit", "#health", "#training", "#motivation", "#exercise"],
    "Retail": ["#shopping", "#fashion", "#style", "#trendy", "#newproduct", "#sale", "#gadgets", "#tech"]
}

# Sample products by industry
PRODUCTS = {
    "Restaurant": ["Chicken Tacos", "Beef Burrito", "Veggie Bowl", "Nachos Supreme", "Churros", "Horchata"],
    "Fitness": ["Protein Shake", "Yoga Class", "Personal Training", "Group Fitness", "Membership"],
    "Retail": ["Smartphone", "Wireless Earbuds", "Smartwatch", "Laptop", "Tablet", "Smart Speaker"]
}

# Sample authors by platform
AUTHORS = {
    "instagram": ["FoodieLife", "TastyBites", "FitnessFanatic", "WorkoutDaily", "TechReviewer", "GadgetGuru"],
    "youtube": ["FoodChannel", "CookingMaster", "FitnessCoach", "GymLife", "TechTips", "GadgetReviews"],
    "tiktok": ["FoodTok", "RecipeKing", "FitTok", "WorkoutTips", "TechTok", "GadgetHacks"]
}

def generate_sample_data(output_dir, num_days=30):
    """Generate sample data for businesses, accounts, metrics, and content."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate businesses
    businesses_data = BUSINESSES
    with open(os.path.join(output_dir, "businesses.json"), "w") as f:
        json.dump(businesses_data, f, indent=2)
    
    # Generate social accounts
    accounts_data = []
    account_id = 1
    
    for business in businesses_data:
        for platform in PLATFORMS:
            account_name = f"{business['name'].lower().replace(' ', '')}"
            if platform == "instagram":
                account_name = f"@{account_name}"
            elif platform == "youtube":
                account_name = f"{account_name}channel"
            elif platform == "tiktok":
                account_name = f"{account_name}"
                
            accounts_data.append({
                "id": account_id,
                "business_id": business["id"],
                "platform": platform,
                "account_id": f"{platform}_{business['id']}_{account_id}",
                "account_name": account_name
            })
            account_id += 1
    
    with open(os.path.join(output_dir, "social_accounts.json"), "w") as f:
        json.dump(accounts_data, f, indent=2)
    
    # Generate metrics and content for each account
    all_metrics = []
    all_content = []
    instagram_content = []  # Special format for Instagram content
    
    metric_id = 1
    content_id = 1
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)
    
    for account in accounts_data:
        # Generate daily metrics
        current_date = start_date
        followers = random.randint(1000, 10000)
        
        while current_date <= end_date:
            # Random daily change in followers (between -50 and +200)
            follower_change = random.randint(-50, 200)
            followers += follower_change
            
            # Generate metrics for the day
            daily_likes = random.randint(100, 1000)
            daily_comments = random.randint(10, 200)
            daily_shares = random.randint(5, 100)
            daily_views = random.randint(500, 5000)
            
            # Platform-specific metrics
            platform_data = {}
            if account["platform"] == "instagram":
                platform_data = {
                    "reach": random.randint(1000, 5000),
                    "impressions": random.randint(2000, 10000),
                    "profile_views": random.randint(100, 500),
                    "engagement_rate": round(random.uniform(0.01, 0.1), 4)
                }
            elif account["platform"] == "youtube":
                platform_data = {
                    "watch_time_hours": random.randint(100, 1000),
                    "average_view_duration": random.randint(60, 600),
                    "click_through_rate": round(random.uniform(0.01, 0.2), 4),
                    "unique_viewers": random.randint(300, 3000)
                }
            elif account["platform"] == "tiktok":
                platform_data = {
                    "profile_views": random.randint(200, 2000),
                    "video_views": random.randint(1000, 10000),
                    "engagement_rate": round(random.uniform(0.02, 0.15), 4),
                    "average_watch_time": random.randint(5, 60)
                }
            
            metric = {
                "id": metric_id,
                "social_account_id": account["id"],
                "timestamp": current_date.isoformat(),
                "followers": followers,
                "likes": daily_likes,
                "comments": daily_comments,
                "shares": daily_shares,
                "views": daily_views,
                "platform_data": platform_data
            }
            
            all_metrics.append(metric)
            metric_id += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Generate content (posts/videos)
        business = next(b for b in businesses_data if b["id"] == account["business_id"])
        industry = business["industry"]
        
        # Number of content items to generate (between 5 and 15)
        num_content = random.randint(5, 15)
        
        for _ in range(num_content):
            # Random date within the time period
            days_ago = random.randint(0, num_days)
            published_date = end_date - timedelta(days=days_ago)
            
            # Random content type for the platform
            content_type = random.choice(CONTENT_TYPES[account["platform"]])
            
            # Random engagement metrics
            likes = random.randint(50, 500)
            comments = random.randint(5, 100)
            shares = random.randint(2, 50)
            views = random.randint(200, 2000)
            
            # Random product mention
            product = random.choice(PRODUCTS[industry])
            
            # Random hashtags
            num_hashtags = random.randint(2, 5)
            hashtags = random.sample(HASHTAGS[industry], num_hashtags)
            
            # Generate title and description
            if content_type in ["post", "reel", "story"]:
                title = f"Check out our {product}!"
                description = f"Try our amazing {product} today! {' '.join(hashtags)}"
            else:  # video
                title = f"{product} Review | {business['name']}"
                description = f"In this video, we showcase our {product}. Don't forget to like and subscribe! {' '.join(hashtags)}"
            
            # Generate content ID (shortcode for Instagram)
            shortcode = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-', k=11))
            content_uuid = str(uuid.uuid4())
            
            # Generate URLs based on platform
            if account["platform"] == "instagram":
                url = f"https://www.instagram.com/{content_type}/{shortcode}/"
                thumbnail_url = f"https://instagram.fhan5-9.fna.fbcdn.net/v/t51.2885-15/{random.randint(100000000, 999999999)}_{random.randint(10000000000000000, 99999999999999999)}_{random.randint(1000000000000000, 9999999999999999)}_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=instagram.fhan5-9.fna.fbcdn.net&_nc_cat=1"
            else:
                url = f"https://example.com/{account['platform']}/{content_uuid}"
                thumbnail_url = f"https://example.com/{account['platform']}/thumbnails/{content_uuid}.jpg"
            
            # Duration for video content
            duration = None
            if content_type in ["video", "reel", "short"]:
                if account["platform"] == "instagram":
                    duration = round(random.uniform(5.0, 30.0), 1)
                elif account["platform"] == "youtube":
                    duration = random.randint(60, 900)
                elif account["platform"] == "tiktok":
                    duration = random.randint(15, 60)
            
            # Additional metadata
            metadata = {}
            if account["platform"] == "instagram":
                media_type = "IMAGE" if content_type == "post" else "VIDEO"
                metadata = {
                    "media_type": media_type,
                    "hashtags": hashtags,
                    "mentions": [],
                    "location": "Store Location" if random.random() > 0.5 else None
                }
                
                # Create Instagram-specific format
                author = random.choice(AUTHORS["instagram"])
                media_id = str(random.randint(1000000000000000000, 9999999999999999999))
                media_url = f"https://instagram.fhan5-8.fna.fbcdn.net/o1/v/t16/f2/m86/AQO6S0y0h33BE7XMwyAmvqk5g5zA27kDkX9bvggKckX2Q0lteaJ13TK768Zmf1J2BMsuAHAgQMqirHkc0wD2dRtYPl7WYqiaG8ii2sQ.mp4?stp=dst-mp4&efg=eyJxZV9ncm91cHMiOiJbXCJpZ193ZWJfZGVsaXZlcnlfdnRzX290ZlwiXSIsInZlbmNvZGVfdGFnIjoidnRzX3ZvZF91cmxnZW4uY2xpcHMuYzIuNzIwLmJhc2VsaW5lIn0&_nc_cat=106&vs=3928298130744648_1697374883&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC85NjRBQkU0REU4MzU2OERBNURDRUU3QzNBQjI0RkZCQ192aWRlb19kYXNoaW5pdC5tcDQVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dDbmRfaHdMRVByT2RqNENBSWo5ZG1BUUhlc01icV9FQUFBRhUCAsgBACgAGAAbABUAACb27NidzfyhQBUCKAJDMywXQCZmZmZmZmYYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HAA%3D%3D&ccb=9-4&oh=00_AYEpOQgbGhYbN6iIv63Zg5CBMYq2Lo240hZCdFyrM-P6Eg&oe=67E0F560&_nc_sid=10d13b"
                
                instagram_data = {
                    "url": url,
                    "result": {
                        "url": url,
                        "source": "instagram",
                        "title": title,
                        "author": author,
                        "shortcode": shortcode,
                        "thumbnail": thumbnail_url,
                        "duration": duration,
                        "medias": [
                            {
                                "id": media_id,
                                "url": media_url,
                                "quality": "1080-1920p",
                                "type": "video" if media_type == "VIDEO" else "image",
                                "extension": "mp4" if media_type == "VIDEO" else "jpg"
                            }
                        ],
                        "type": "single",
                        "error": False,
                        "time_end": random.randint(500, 2000)
                    }
                }
                
                instagram_content.append(instagram_data)
                
            elif account["platform"] == "youtube":
                metadata = {
                    "duration": duration,
                    "tags": hashtags,
                    "category_id": "22",
                    "definition": "hd",
                    "caption": "true" if random.random() > 0.7 else "false"
                }
            elif account["platform"] == "tiktok":
                metadata = {
                    "duration": duration,
                    "hashtags": hashtags,
                    "music": {"name": f"Popular Song {random.randint(1, 100)}"},
                    "video_format": "vertical",
                    "region": "global"
                }
            
            # Standard content format for database
            content = {
                "id": content_id,
                "social_account_id": account["id"],
                "content_id": shortcode if account["platform"] == "instagram" else content_uuid,
                "content_type": content_type,
                "title": title,
                "description": description,
                "url": url,
                "thumbnail_url": thumbnail_url,
                "published_at": published_date.isoformat(),
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "views": views,
                "duration": duration,
                "content_metadata": metadata,
                # Add a reference to a sample video file that would be processed
                "video_file": f"sample_videos/{account['platform']}_{content_type}_{content_id}.mp4" if content_type in ["video", "reel", "short"] else None
            }
            
            all_content.append(content)
            content_id += 1
    
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(all_metrics, f, indent=2)
    
    with open(os.path.join(output_dir, "content.json"), "w") as f:
        json.dump(all_content, f, indent=2)
        
    # Save Instagram-specific content format
    with open(os.path.join(output_dir, "instagram_content.json"), "w") as f:
        json.dump(instagram_content, f, indent=2)
    
    print(f"Generated sample data in {output_dir}:")
    print(f"- {len(businesses_data)} businesses")
    print(f"- {len(accounts_data)} social accounts")
    print(f"- {len(all_metrics)} metric records")
    print(f"- {len(all_content)} content items")

if __name__ == "__main__":
    generate_sample_data("./data")
