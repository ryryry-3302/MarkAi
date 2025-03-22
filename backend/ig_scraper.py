from apify_client import ApifyClient
import requests
import re

# Initialize the ApifyClient with your API token
apify_token = ""
client = ApifyClient(apify_token)

# Prepare the Actor input
run_input = { "links": ["https://www.instagram.com/reel/DHfdcysMAEZ/"] }

# Run the Actor and wait for it to finish
run = client.actor("Fj1zYgto86GELL443").call(run_input=run_input)

# Fetch and process Actor results from the run's dataset
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
    
    # Check if the result contains media URLs
    if 'result' in item and 'medias' in item['result'] and item['result']['medias']:
        for i, media in enumerate(item['result']['medias']):
            if 'url' in media and media['url']:
                # Get title from result and clean it for use as filename
                title = item['result'].get('title', '')
                if not title:
                    # Fallback to shortcode if no title
                    title = item['result'].get('shortcode', 'unknown')
                
                # Clean the title to make it suitable for a filename
                # Remove invalid filename characters and limit length
                clean_title = re.sub(r'[\\/*?:"<>|]', "", title)  # Remove invalid filename chars
                clean_title = clean_title[:100]  # Limit length
                
                # Create filename with title
                file_extension = media.get('extension', 'mp4')
                filename = f"{clean_title}.{file_extension}"
                
                # Download the file
                try:
                    print(f"Downloading {media['url']} to {filename}...")
                    response = requests.get(media['url'], stream=True)
                    response.raise_for_status()
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"Successfully downloaded to {filename}")
                except Exception as e:
                    print(f"Error downloading {media['url']}: {e}")
    else:
        print("No media URLs found in the result")