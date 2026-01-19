"""Script to fetch QUP-606 issue details using the Atlassian MCP server client."""
import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from atlassian_mcp_server.clients import JiraClient, AtlassianConfig

# Load config from config.json
config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    config_data = json.load(f)

config = AtlassianConfig(
    site_url=config_data["ATLASSIAN_SITE_URL"],
    client_id=config_data["ATLASSIAN_CLIENT_ID"],
    client_secret=config_data["ATLASSIAN_CLIENT_SECRET"],
)

# Try to load saved credentials
creds_file = Path.home() / ".atlassian_mcp_credentials.json"
if creds_file.exists():
    with open(creds_file) as f:
        creds = json.load(f)
        config.access_token = creds.get("access_token")
        config.refresh_token = creds.get("refresh_token")

client = JiraClient(config)

async def get_qup606():
    """Fetch QUP-606 issue details."""
    try:
        issue = await client.jira_get_issue("QUP-606")
        print(json.dumps(issue, indent=2))
        return issue
    except Exception as e:
        print(f"Error fetching QUP-606: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        if hasattr(e, "__dict__"):
            print(f"Error details: {json.dumps(e.__dict__, indent=2, default=str)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    asyncio.run(get_qup606())
