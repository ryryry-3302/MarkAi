from apify_client import ApifyClient
import json
import requests
import re
import os
from operator import itemgetter

# Initialize the ApifyClient with your API token
apify_token = "apify_api_BO1DQUOl5jfHrV1dpD25hRRIqlEORp2E7I2e"
client = ApifyClient(apify_token)

def load_influencers_data(json_file_path):
    """Load influencers data from the JSON file and extract those with follower counts."""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    influencers = []
    for entry in data:
        # Check if instagram_data exists and has followersCount
        if entry.get('instagram_data') and entry['instagram_data'].get('followersCount'):
            influencer = {
                'username': entry['username'],
                'followers_count': entry['instagram_data']['followersCount'],
                'id': entry['instagram_data'].get('id', '')
            }
            influencers.append(influencer)
    
    return influencers

def get_top_influencers(influencers, count=5):
    """Get the top influencers by follower count."""
    # Sort influencers by followers_count in descending order
    sorted_influencers = sorted(influencers, key=itemgetter('followers_count'), reverse=True)
    return sorted_influencers[:count]

def get_reels_for_influencer(username, count=3):
    """Get specified number of reels for an influencer."""
    # Prepare the Actor input to specifically look for reels/videos
    run_input = {
        "username": [username],
        "resultsLimit": 10,  # Fetch more than needed to ensure we get enough reels
    }
    
    # Run the Actor and wait for it to finish
    run = client.actor("xMc5Ga1oCONPmWJIa").call(run_input=run_input)
    
    # Fetch and process Actor results from the run's dataset
    reels = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # Check if the post is a video/reel
        if ('videoUrl' in item and item['videoUrl']) or (item.get('type') == 'Video'):
            reels.append(item)
            if len(reels) >= count:
                break
    
    return reels

def download_reel(reel, influencer_username, output_dir):
    """Download a reel and save it to the specified directory."""
    # Create directory for influencer if it doesn't exist
    influencer_dir = os.path.join(output_dir, influencer_username)
    os.makedirs(influencer_dir, exist_ok=True)
    
    # Get caption from result and clean it for use as filename
    caption = reel.get('caption', '')
    if not caption:
        # Fallback to shortcode if no caption
        caption = reel.get('shortCode', 'unknown')
    
    # Clean the caption to make it suitable for a filename
    clean_caption = re.sub(r'[\\/*?:"<>|]', "", caption)  # Remove invalid filename chars
    clean_caption = clean_caption[:50]  # Limit length
    
    # Create filename with caption
    filename = f"{clean_caption}.mp4"
    filepath = os.path.join(influencer_dir, filename)
    
    # Get video URL
    video_url = reel.get('videoUrl')
    if not video_url:
        print(f"No video URL found for reel {reel.get('shortCode')}")
        return None
    
    # Download the file
    try:
        print(f"Downloading {video_url} to {filepath}...")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")
        return None

def main():
    # Path to your JSON file with influencer data
    json_file_path = 'combined_data.json'
    
    # Output directory for downloaded reels
    output_dir = 'influencer_reels'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load influencers data
    influencers = load_influencers_data(json_file_path)
    
    # Get top 5 influencers by follower count
    top_influencers = get_top_influencers(influencers, count=5)
    
    # Print top influencers
    print("Top 5 Influencers by Follower Count:")
    for i, influencer in enumerate(top_influencers, 1):
        print(f"{i}. {influencer['username']} - {influencer['followers_count']} followers")
    
    # Create a results dictionary
    results = []
    
    # Get and download 3 reels for each top influencer
    for influencer in top_influencers:
        username = influencer['username']
        print(f"\nFetching reels for {username}...")
        
        reels = get_reels_for_influencer(username, count=3)
        
        influencer_result = {
            'username': username,
            'followers_count': influencer['followers_count'],
            'reels': []
        }
        
        for reel in reels:
            # Download the reel
            filepath = download_reel(reel, username, output_dir)
            
            # Add reel info to results
            reel_info = {
                'shortCode': reel.get('shortCode', ''),
                'caption': reel.get('caption', ''),
                'likesCount': reel.get('likesCount', 0),
                'commentsCount': reel.get('commentsCount', 0),
                'url': reel.get('url', ''),
                'local_path': filepath
            }
            influencer_result['reels'].append(reel_info)
        
        results.append(influencer_result)
    
    # Save results to JSON file
    results_file = os.path.join(output_dir, 'top_influencers_reels.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {results_file}")

if __name__ == "__main__":
    main() 