from apify_client import ApifyClient
from pprint import pprint

# apify_token = "apify_api_EvkTzmY0mqZ4yiL1Ij6DLqovp7LJTT4w56A8"
apify_token = "apify_api_Wb5WgDS2Pa9XlecQfyRJKr3dP37GLW2tscch"
client = ApifyClient(apify_token)

# Prepare the Actor input
run_input = {
    "keyword": "mexican restaurant",
    "location": "San Francisco",
    "country": "us",
    "language": "en",
    "maxLeads": 10,
    "proxyConfiguration": { "useApifyProxy": True },
}

# Run the Actor and wait for it to finish
run = client.actor("ch6gZoTBdOqyaVuVw").call(run_input=run_input)
leads = []
# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
    leads.append(item)
print("===========================")
pprint(leads)