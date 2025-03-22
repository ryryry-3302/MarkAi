import json
from apify_client import ApifyClient

def get_instagram_data(usernames):
    """
    Fetch Instagram profile data for a list of usernames using Apify
    """
    apify_token = "apify_api_BO1DQUOl5jfHrV1dpD25hRRIqlEORp2E7I2e"
    client = ApifyClient(apify_token)
    
    # Filter out empty usernames or placeholders
    valid_usernames = [username for username in usernames if username and username != "-"]
    
    if not valid_usernames:
        return []
    
    # Prepare the Actor input
    run_input = {"usernames": valid_usernames}
    
    # Run the Actor and wait for it to finish
    run = client.actor("dSCLg0C3YEZ83HzYX").call(run_input=run_input)
    
    # Fetch Actor results from the run's dataset
    results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return results

def main():
    # Load the input JSON data
    with open('leads.json', 'r') as file:
        leads_data = json.load(file)
    
    # Extract usernames from the data
    usernames = [lead.get('username', '') for lead in leads_data]
    
    # Get Instagram data for these usernames
    instagram_data = get_instagram_data(usernames)
    
    # Create a mapping of username to Instagram data for easy lookup
    instagram_data_map = {item.get('username', '').lower(): item for item in instagram_data}
    
    # Combine the original data with the Instagram data
    combined_data = []
    for lead in leads_data:
        username = lead.get('username', '').lower()
        lead_copy = lead.copy()
        
        # Add Instagram data if available
        if username and username != '-' and username in instagram_data_map:
            insta_data = instagram_data_map[username]
            lead_copy['instagram_data'] = insta_data
        else:
            lead_copy['instagram_data'] = None
            
        combined_data.append(lead_copy)
    
    # Output the combined data as JSON
    with open('combined_data.json', 'w') as outfile:
        json.dump(combined_data, outfile, indent=2)
    
    print(f"Combined data saved to combined_data.json")
    print(f"Processed {len(leads_data)} leads, found Instagram data for {len(instagram_data)} profiles")

if __name__ == "__main__":
    main()