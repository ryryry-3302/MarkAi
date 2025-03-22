from apify_client import ApifyClient
import json
import os
import time
import pprint

# Initialize the ApifyClient with your API token
apify_token = "apify_api_BO1DQUOl5jfHrV1dpD25hRRIqlEORp2E7I2e"
client = ApifyClient(apify_token)

# Create a directory for results if it doesn't exist
results_dir = "instagram_results"
os.makedirs(results_dir, exist_ok=True)

def find_instagram_leads(keyword, location, max_leads=5):
    """Find Instagram profiles based on keyword and location"""
    print(f"Finding Instagram profiles for '{keyword}' in '{location}'...")
    
    # Prepare the Actor input for the leads agent
    run_input = {
        "keyword": keyword,
        "location": location,
        "country": "us",
        "language": "en",
        "maxLeads": max_leads,
        "proxyConfiguration": { "useApifyProxy": True },
    }

    print("\nLeads Agent Input:")
    pprint.pprint(run_input)

    # Run the Actor and wait for it to finish
    run = client.actor("ch6gZoTBdOqyaVuVw").call(run_input=run_input)
    
    print(f"\nLeads Agent Run Info:")
    pprint.pprint(run)
    
    # Extract usernames and lead information from results
    leads = []
    usernames = []
    
    print("\nLeads Agent Results:")
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        leads.append(item)
        print("\n--- Lead Item ---")
        pprint.pprint(item)
        print("----------------")
        
        print(f"Found lead: {item.get('name', 'Unknown')}")
        
        if 'instagram' in item and item['instagram']:
            # Extract username from Instagram URL or handle
            instagram = item['instagram']
            if 'instagram.com/' in instagram:
                username = instagram.split('instagram.com/')[1].split('/')[0].split('?')[0]
            else:
                username = instagram.lstrip('@')
            
            if username and username not in usernames:
                usernames.append(username)
                print(f"  Instagram username: {username}")
    
    # Save leads to a JSON file
    leads_file = os.path.join(results_dir, f"leads_{keyword}_{location}.json")
    with open(leads_file, 'w') as f:
        json.dump(leads, f, indent=2)
    
    print(f"Saved {len(leads)} leads to {leads_file}")
    return usernames, leads

def get_profile_details(usernames):
    """Get detailed information about Instagram profiles"""
    print(f"Getting detailed information for {len(usernames)} profiles...")
    
    # Prepare the Actor input for the profile info scraper
    run_input = { "usernames": usernames }

    print("\nProfile Info Scraper Input:")
    pprint.pprint(run_input)

    # Run the Actor and wait for it to finish
    run = client.actor("dSCLg0C3YEZ83HzYX").call(run_input=run_input)
    
    print(f"\nProfile Info Scraper Run Info:")
    pprint.pprint(run)
    
    # Process and return profile details
    profiles = []
    
    print("\nProfile Info Scraper Results:")
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        profiles.append(item)
        print("\n--- Profile Item ---")
        pprint.pprint(item)
        print("-------------------")
        
        username = item.get('username', '')
        if username:
            print(f"Got details for {username}: {item.get('fullName', 'Unknown')} - {item.get('biography', 'No bio')[:50]}...")
    
    # Save profiles to a JSON file
    profiles_file = os.path.join(results_dir, f"profiles_{'_'.join(usernames[:3])}.json")
    with open(profiles_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    print(f"Saved {len(profiles)} profile details to {profiles_file}")
    return profiles

def main():
    # Find Instagram profiles based on keyword and location
    keyword = input("Enter search keyword (e.g., 'mexican restaurant'): ")
    location = input("Enter location (e.g., 'San Francisco'): ")
    max_leads = int(input("Enter maximum number of profiles to find (e.g., 5): "))
    
    usernames, leads = find_instagram_leads(keyword, location, max_leads)
    
    if not usernames:
        print("No Instagram profiles found. Exiting.")
        return
    
    # Get detailed information about the profiles
    profiles = get_profile_details(usernames)
    
    # Generate a combined report
    report = {
        "search_criteria": {
            "keyword": keyword,
            "location": location,
            "max_leads": max_leads
        },
        "leads_found": len(leads),
        "instagram_profiles_found": len(usernames),
        "profile_details_retrieved": len(profiles),
        "usernames": usernames
    }
    
    report_file = os.path.join(results_dir, f"report_{keyword}_{location}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nAll done! Results have been saved to the '{results_dir}' directory.")
    print(f"Summary report saved to {report_file}")

if __name__ == "__main__":
    main()