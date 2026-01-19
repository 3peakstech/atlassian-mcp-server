import asyncio
import json
from pathlib import Path
from atlassian_mcp_server.clients import JiraClient, AtlassianConfig

creds_file = Path.home() / '.atlassian_mcp_credentials.json'
creds = json.load(open(creds_file))

config = AtlassianConfig(
    site_url=creds['site_url'],
    client_id=creds['client_id'],
    client_secret=creds['client_secret'],
    access_token=creds.get('access_token'),
    refresh_token=creds.get('refresh_token')
)

client = JiraClient(config)

async def test_search():
    cloud_id = await client.get_cloud_id()
    url = f"{client.jira_base}/{cloud_id}/rest/api/3/search/jql"
    data = {
        "jql": "order by created DESC",
        "maxResults": 5,
        "fields": ["summary", "status", "assignee", "priority", "issuetype", "description"],
    }
    
    response = await client.make_request("POST", url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        result = response.json().get("issues", [])
        print(f'Found {len(result)} issues')
        print(json.dumps([{'key': i.get("key"), 'summary': i.get("fields", {}).get("summary")} for i in result], indent=2))
    else:
        print(f"Error response: {response.text}")

try:
    asyncio.run(test_search())
except Exception as e:
    print(f'Error: {e}')
    print(f'Error type: {type(e).__name__}')
    if hasattr(e, 'to_dict'):
        print(f'Error details: {json.dumps(e.to_dict(), indent=2)}')
