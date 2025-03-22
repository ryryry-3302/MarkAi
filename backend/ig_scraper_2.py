from apify_client import ApifyClient
import requests
import re

# Initialize the ApifyClient with your API token
apify_token = "apify_api_BO1DQUOl5jfHrV1dpD25hRRIqlEORp2E7I2e"
client = ApifyClient(apify_token)

# Prepare the Actor input
run_input = {
    "username": ["natgeo"],
    "resultsLimit": 1,
}

# Run the Actor and wait for it to finish
run = client.actor("xMc5Ga1oCONPmWJIa").call(run_input=run_input)

# Fetch and process Actor results from the run's dataset
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
    
    # Check if the post is a video
    if 'videoUrl' in item and item['videoUrl']:
        # Get caption from result and clean it for use as filename
        caption = item.get('caption', '')
        if not caption:
            # Fallback to shortcode if no caption
            caption = item.get('shortCode', 'unknown')
        
        # Clean the caption to make it suitable for a filename
        # Remove invalid filename characters and limit length
        clean_caption = re.sub(r'[\\/*?:"<>|]', "", caption)  # Remove invalid filename chars
        clean_caption = clean_caption[:100]  # Limit length
        
        # Create filename with caption
        filename = f"{clean_caption}.mp4"
        
        # Download the file
        try:
            print(f"Downloading {item['videoUrl']} to {filename}...")
            response = requests.get(item['videoUrl'], stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Successfully downloaded to {filename}")
        except Exception as e:
            print(f"Error downloading {item['videoUrl']}: {e}")
    
    # Check if the post has images
    elif 'displayUrl' in item and item['displayUrl']:
        # Get caption from result and clean it for use as filename
        caption = item.get('caption', '')
        if not caption:
            # Fallback to shortcode if no caption
            caption = item.get('shortCode', 'unknown')
        
        # Clean the caption to make it suitable for a filename
        # Remove invalid filename characters and limit length
        clean_caption = re.sub(r'[\\/*?:"<>|]', "", caption)  # Remove invalid filename chars
        clean_caption = clean_caption[:100]  # Limit length
        
        # Create filename with caption
        filename = f"{clean_caption}.jpg"
        
        # Download the file
        try:
            print(f"Downloading {item['displayUrl']} to {filename}...")
            response = requests.get(item['displayUrl'], stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Successfully downloaded to {filename}")
        except Exception as e:
            print(f"Error downloading {item['displayUrl']}: {e}")
    
    # Check if the post has child posts (carousel)
    elif 'childPosts' in item and item['childPosts']:
        for i, child in enumerate(item['childPosts']):
            # Get caption from result and clean it for use as filename
            caption = item.get('caption', '')
            if not caption:
                # Fallback to shortcode if no caption
                caption = item.get('shortCode', 'unknown')
            
            # Clean the caption to make it suitable for a filename
            # Remove invalid filename characters and limit length
            clean_caption = re.sub(r'[\\/*?:"<>|]', "", caption)  # Remove invalid filename chars
            clean_caption = clean_caption[:100]  # Limit length
            
            # Determine file extension based on media type
            if 'videoUrl' in child and child['videoUrl']:
                file_extension = 'mp4'
                media_url = child['videoUrl']
            else:
                file_extension = 'jpg'
                media_url = child.get('displayUrl', '')
            
            # Create filename with caption and index
            filename = f"{clean_caption}_{i+1}.{file_extension}"
            
            # Download the file if media URL exists
            if media_url:
                try:
                    print(f"Downloading {media_url} to {filename}...")
                    response = requests.get(media_url, stream=True)
                    response.raise_for_status()
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"Successfully downloaded to {filename}")
                except Exception as e:
                    print(f"Error downloading {media_url}: {e}")
    else:
        print("No media found in the post")